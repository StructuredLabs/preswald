import ast
import copy
import inspect
import logging
import textwrap
from collections import defaultdict

from preswald.engine.transformers.frame_context import FrameContext as Frame
from preswald.interfaces import components
from preswald.interfaces.render.registry import (
    get_component_type_for_mimetype,
    get_display_dependency_resolvers,
    get_display_detectors,
    get_display_methods,
    get_display_renderers,
    get_output_stream_calls,
    get_return_renderers,
    get_return_type_hint,
    register_display_dependency_resolver,
    register_display_method,
    register_mimetype_component_type,
    register_output_stream_function,
    register_return_renderer,
)
from preswald.interfaces.render.error_registry import register_error
from preswald.utils import (
    generate_stable_atom_name_from_component_id,
    generate_stable_id,
)


logger = logging.getLogger(__name__)

ARTIFICIAL_LINE_NUMBER_START = 100_000 # Used when node call has no lineno attribute. Assumes that nobody has a user script with code on line >= 100,000

class AstHaltError(Exception):
    """Raised when AST transformation must be aborted immediately."""
    pass


class AutoAtomTransformer(ast.NodeTransformer):
    """
    AST transformer that automatically lifts Preswald component calls into reactive atoms.

    This transformer analyzes the user script, identifies known Preswald components,
    generates stable component IDs and atom names, and rewrites the AST to wrap
    component calls inside decorated atom functions.

    Attributes:
        filename (str): The name of the file being transformed (used for callsite hints).
        atoms (list[str]): List of generated atom names.
        _all_function_defs (list[ast.FunctionDef]): All top-level function definitions found.
        current_function (ast.FunctionDef | None): Function currently being visited.
        dependencies (dict[str, set[str]]): Atom dependencies tracked during traversal.
        helper_counter (int): Counter for generating unique callsite hints when needed.
        generated_atoms (list[ast.FunctionDef]): List of new atom functions generated.
        variable_to_atom (dict[str, str]): Mapping from variable names to atom names.
        known_components (set[str]): Names of known built-in Preswald components.
    """

    def __init__(self, filename: str = "<script>"):
        self.filename = filename
        self.current_function = None
        self.dependencies = {}
        self.known_components = self._discover_known_components()
        self._all_function_defs = []
        self._blackbox_lifted_functions: set[str] = set()
        self._top_level_user_function_calls = []
        self._frames: list[Frame] = []
        self.atoms = []
        self._used_linenos = set()
        self._artificial_lineno = ARTIFICIAL_LINE_NUMBER_START
        self._in_function_body = False
        self.import_aliases = {}
        self.name_aliases: dict[str, str] = {}
        self._variable_class_map = {}
        self._module: ast.Module | None = None
        self._used_display_renderer_fns: set[str] = set()

    @property
    def _current_frame(self) -> Frame:
        return self._frames[-1]

    @property
    def _module_frame(self) -> Frame:
        return self._frames[0]

    def _reset(self):
        self.current_function = None
        self.dependencies = {}
        self._all_function_defs = []
        self._blackbox_lifted_functions: set[str] = set()
        self._top_level_user_function_calls = []

        self._frames = [Frame()]
        self.atoms = []
        self._used_linenos = set()
        self._artificial_lineno = ARTIFICIAL_LINE_NUMBER_START
        self.known_components = self._discover_known_components()
        self._in_function_body = False
        self.import_aliases = {}
        self._name_aliases: dict[str, str] = {}
        self._variable_class_map = {}
        self._module: ast.Module | None = None
        self._used_display_renderer_fns: set[str] = set()

    def _safe_register_error(self,
        *,
        node: ast.AST | None = None,
        lineno: int | None = None,
        message: str,
        component_id: str | None = None,
        atom_name: str | None = None,
        fallback_source: str = "",
        extra_context: str = "",
    ):
        """
        Safely registers an error, using `ast.unparse` if possible, and falling back
        to `ast.dump` or a provided `fallback_source`.

        Args:
            node: Optional AST node to derive source from.
            lineno: Optional explicit line number.
            message: Error message.
            component_id: Optional component ID.
            atom_name: Optional atom name.
            fallback_source: Optional string to use if unparsing fails.
            extra_context: Optional additional debug info.
        """
        if node is not None:
            try:
                source = ast.unparse(node)
            except Exception:
                logger.debug(f"[AST] Failed to unparse node, falling back to ast.dump: {e}")
                source = ast.dump(node)
        else:
            source = fallback_source or "<source unavailable>"

        if extra_context:
            message = f"{message} | Context: {extra_context}"

        register_error(
            type='ast_transform',
            filename=self.filename,
            lineno=lineno or getattr(node, "lineno", 0), # TODO: upate this to default to artificial lineno
            message=message,
            source=source,
            component_id=component_id,
            atom_name=atom_name,
        )


    def _discover_known_components(self) -> set[str]:
        """
        Returns a set of known component names (bare and module-qualified)
        based on known component registry and user imported names.
        """
        known_components = set()

        for name in dir(components):
            obj = getattr(components, name, None)
            if getattr(obj, "_preswald_component_type", None) is not None:
                known_components.add(name)
        return known_components

    def _is_known_component_call(self, call_node: ast.Call) -> bool:
        if isinstance(call_node.func, ast.Name):
            func_id = call_node.func.id
            return (
                func_id in self.known_components
                or func_id in self._name_aliases.values()
            )
        elif isinstance(call_node.func, ast.Attribute):
            receiver = call_node.func.value
            attr = call_node.func.attr

            if isinstance(receiver, ast.Name):
                alias = receiver.id

                # Case 1: exact alias matches known preswald import
                modname = self.import_aliases.get(alias)
                if modname:
                    if modname == "preswald":
                        return attr in self.known_components

                    # fallback to check that modname is from preswald
                    if modname.startswith("preswald"):
                        return attr in self.known_components

        return False

    def _contains_known_component_call(self, stmt: ast.FunctionDef) -> bool:
        """
        Returns True if the given function definition contains any calls to known components.
        """
        class ComponentCallVisitor(ast.NodeVisitor):
            def __init__(self, known_components: set[str]):
                self.known_components = known_components
                self.found = False

            def visit_Call(self, node: ast.Call):  # noqa: N802
                if isinstance(node.func, ast.Name) and node.func.id in self.known_components:
                    self.found = True
                elif isinstance(node.func, ast.Attribute):
                    # Handle namespaced calls like preswald.text
                    try:
                        if isinstance(node.func.value, ast.Name):
                            full_name = f"{node.func.value.id}.{node.func.attr}"
                            if full_name in self.known_components:
                                self.found = True
                    except Exception as e:
                        register_error(
                            type="ast_transform",
                            filename=self.filename,
                            lineno=node.lineno,
                            message=f"Error analyzing namespaced component call: {e}",
                            source=ast.unparse(node),
                            component_id=None,
                            atom_name=None,
                        )
                        logger.error("[AST] Failed to analyze namespaced component call", exc_info=True)

                if not self.found:
                    self.generic_visit(node)

        visitor = ComponentCallVisitor(self.known_components)
        visitor.visit(stmt)
        return visitor.found

    def _get_stable_lineno(self, call_node: ast.Call, fallback_context: str) -> int:
        """
        Returns a stable line number for a given AST call node.

        If the node lacks a real lineno, such is the case for synthetic nodes, then a unique artificial one is assigned.
        Line number uniqueness is important to avoid collisions when generating deterministic component/atom
        names based on source location.

        Args:
            call_node: The AST Call node.
            fallback_context: Description of the context for logging if lineno is missing.

        Returns:
            A unique and stable line number.
        """
        lineno = getattr(call_node, "lineno", None)
        if lineno is None:
            if logger.isEnabledFor(logging.WARNING):
                logger.warning(f"[AST] {fallback_context} missing lineno - assigning artificial line number")
            while self._artificial_lineno in self._used_linenos:
                self._artificial_lineno += 1
            lineno = self._artificial_lineno

        self._used_linenos.add(lineno)
        return lineno

    def _generate_component_metadata(self, body: list[ast.stmt]) -> dict[int, tuple[str, str]]:
        """
        Scans the top-level statements in the user script to identify calls to known Preswald components.

        For each component call, this function generates:
        - A stable `component_id` based on the component name and callsite location
        - A corresponding `atom_name` that will be used for lifting into a reactive atom

        The returned mapping allows later AST transforms to assign consistent and reproducible identities
        to component atoms, which is critical for deterministic DAG wiring in the reactive runtime.

        Args:
            body: A list of top-level AST statements in the user script.

        Returns:
            A mapping from the `id()` of each detected component `ast.Call` node to its
            `(component_id, atom_name)` pair.
        """
        component_to_atom_name = {}

        for stmt in body:
            # Skip function bodies entirely
            if isinstance(stmt, ast.FunctionDef):
                logger.debug(f'[DEBUG] skipping _generate_component_metadata for {stmt.name=}')
                continue

            call_node = stmt.value if isinstance(stmt, ast.Expr) else getattr(stmt, "value", None)

            if isinstance(call_node, ast.Call):
                func = call_node.func
                try:
                    if isinstance(call_node.func, ast.Name):
                        func_name = func.id
                        if func_name in self.known_components:
                            lineno = self._get_stable_lineno(call_node, f"Call to {func_name}")
                            callsite_hint = f"{self.filename}:{lineno}"
                            component_id = generate_stable_id(func_name, callsite_hint=callsite_hint)
                            atom_name = generate_stable_atom_name_from_component_id(component_id)

                            component_to_atom_name[id(call_node)] = (component_id, atom_name)

                            if logger.isEnabledFor(logging.DEBUG):
                                logger.info(f"[AST] Discovered component call {func_name=} {component_id=} {atom_name=}")
                except Exception as e:
                    register_error(
                        type="ast_transform",
                        filename=self.filename,
                        lineno=getattr(stmt, "lineno", 0),
                        message=f"Failed to extract component metadata: {e}",
                        source=ast.unparse(stmt),
                        component_id=None,
                        atom_name=None,
                    )
                    logger.error("[AST] Failed to generate component metadata", exc_info=True)

        return component_to_atom_name

    def _register_variable_bindings(self, stmt: ast.Assign, atom_name: str):
        """
        Registers variables assigned in the given statement as being produced by the specified atom.

        This updates `self.variable_to_atom` to map each variable name (on the LHS of the assignment)
        to the reactive atom responsible for computing its value. This mapping is later used for
        dependency resolution when wiring the DAG.

        Args:
            stmt: An `ast.Assign` node representing the assignment statement.
            atom_name: The name of the atom that produces the assigned value.
        """
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                self._current_frame.variable_to_atom[target.id] = atom_name
                logger.debug(f"[AST] bound variable to atom {target.id=} {atom_name=}")

    def _uses_known_atoms(self, stmt: ast.stmt, variable_map: dict[str, str] | None = None) -> bool:
        """
        Detects if a statement uses any reactive (atom-bound) variables.

        This method checks whether the given AST statement references any variable
        that maps to an existing atom. This is used to determine whether a statement
        should be lifted into a reactive atom, such as consumer expressions or augmented
        assignments with reactive inputs.

        Args:
            stmt (ast.stmt): The statement to inspect.
            variable_map (dict[str, str] | None): Optional override of variable-to-atom map;
                if not provided, defaults to `self.variable_to_atom`.

        Returns:
            bool: True if the statement depends on one or more atoms.
        """
        variable_map = variable_map or self._current_frame.variable_to_atom

        class AtomUsageVisitor(ast.NodeVisitor):
            def __init__(self, variable_map: dict[str, str]):
                self.variable_map = variable_map
                self.found = False

            def visit_Name(self, node: ast.Name): # noqa: N802
                if isinstance(node.ctx, ast.Load) and node.id in self.variable_map:
                    self.found = True

            def generic_visit(self, node):
                if not self.found:
                    super().generic_visit(node)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[AST] _uses_known_atoms: stmt={ast.dump(stmt)}")
            logger.debug(f"[AST] _uses_known_atoms: variable_map keys={list(variable_map.keys())}")

        visitor = AtomUsageVisitor(variable_map)
        visitor.visit(stmt)

        logger.debug(f"[AST] _uses_known_atoms: found={visitor.found}")

        return visitor.found

    def _find_unique_dependencies(
        self, expr: ast.expr,
        variable_map: dict[str, str],
        *,
        stmt: ast.stmt | None = None,
        component_id: str | None = None,
        atom_name: str | None = None,
        context: str = ""
        ) -> tuple[list[str], list[str]]:
        """
        Resolve reactive dependencies for a given expression node, and optionally
        register an error if no dependencies can be found despite known reactive usage.

        This function analyzes the given AST expression to identify variable names
        that are mapped to reactive atoms, and returns:
          - An order preserving list of unique atom names (`callsite_deps`)
          - The original variable names (`dep_names`) they were derived from

        If no dependencies are found and the provided `stmt` uses known atom bound variables,
        a structured transformation error is registered using `_safe_register_error`.

        Args:
            expr: The AST expression node to analyze for dependencies.
            variable_map: A mapping of variable names to reactive atom names.
            stmt: (Optional) Full AST statement, used to check for known atom usage
                  and to include as source context in error reporting.
            component_id: (Optional) Stable component ID to include in the error.
            atom_name: (Optional) Atom name to include in the error.
            context: (Optional) Human-readable context or phase label for diagnostics.

        Returns:
            A tuple:
                - callsite_deps: List of atom names that the expression depends on.
                - dep_names: List of original variable names referenced in the expression.
        """
        callsite_deps, dep_names = self._find_dependencies(expr, variable_map)
        if not callsite_deps and stmt is not None:
            if self._uses_known_atoms(stmt, variable_map=variable_map):
                self._safe_register_error(
                    node=stmt,
                    message="Could not determine any reactive dependencies.",
                    component_id=component_id,
                    atom_name=atom_name,
                    extra_context= f"stmt={ast.dump(stmt)}" if logger.isEnabledFor(logging.DEBUG) else context or "dependency extraction",
                )

        logger.debug(f"[AST] _find_dependencies returned: {callsite_deps=} {dep_names=}")

        seen_atoms: set[str] = set()
        unique_callsite_deps: list[str] = []

        for var in dep_names:
            atom = variable_map.get(var)
            if atom is None:
                logger.warning(f"[AST] Unresolved variable during dependency extraction: {var}")
                continue
            if atom not in seen_atoms:
                unique_callsite_deps.append(atom)
                seen_atoms.add(atom)

        return unique_callsite_deps, dep_names

    def _finalize_atom_deps(self, func: ast.FunctionDef) -> None:
        atom_name = func.name
        if not atom_name:
            return

        for deco in func.decorator_list:
            if (
                isinstance(deco, ast.Call)
                and isinstance(deco.func, ast.Attribute)
                and deco.func.attr == "atom"
            ):
                for kw in deco.keywords:
                    if kw.arg == "dependencies" and isinstance(kw.value, ast.List):
                        extracted = {
                            elt.value
                            for elt in kw.value.elts
                            if isinstance(elt, ast.Constant)
                        }
                        self.dependencies[atom_name] = extracted
                        return

                deps = self.dependencies.get(atom_name)
                if deps:
                    logger.debug(f"[PATCH] Finalizing dependencies for {atom_name}: {sorted(deps)}")
                    deco.keywords.append(ast.keyword(
                        arg="dependencies",
                        value=ast.List(
                            elts=[ast.Constant(value=dep) for dep in sorted(deps)],
                            ctx=ast.Load()
                        )
                    ))
                break

    def _finalize_and_register_atom(
            self,
            atom_name: str,
            component_id: str,
            callsite_deps: list[str],
            call_expr: ast.AST | list[ast.stmt],
            *,
            return_target: str | list[str] | tuple[str, ...] | ast.expr | None = None
        ) -> ast.FunctionDef:
        func = self._build_atom_function(atom_name, component_id, callsite_deps, call_expr, return_target=return_target)
        self._finalize_atom_deps(func)
        self._current_frame.generated_atoms.append(func)
        return func

    def _should_inline_function(self, func_name: str) -> bool:
        """
        Determines whether a user-defined function should be inlined into the callsite.
        For now, always returns False to fall back to blackbox lifting.
        """
        return False

    def _infer_and_register_return_type(self, call_node: ast.Call, atom_name: str) -> None:
        """
        Attempt to infer and register the return type of a function call for use in
        display/render detection. Supports both single and tuple return types.

        Updates `self._current_frame.atom_return_types` if successful.

        Args:
            call_node: The rhs call node from the producer assignment.
            atom_name: The name of the atom being registered.
        """
        func = call_node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            module = func.value.id
            attr = func.attr
            canonical_module = self.import_aliases.get(module, module)
            func_name = f"{canonical_module}.{attr}"

            hint = get_return_type_hint(func_name)
            inferred = hint if hint else func_name

            self._current_frame.atom_return_types[atom_name] = inferred
            logger.debug("[AST] Inferred return type for %s -> %s", atom_name, inferred)
        else:
            if logger.isEnabledFor(logging.DEBUG):
                logger.warning(f"[AST] Could not resolve return type hint for {ast.dump(call_node)}")
            else:
                logger.warning("[AST] Could not resolve return type hint")

    def _is_undecorated(self, node: ast.FunctionDef) -> bool:
        """Return True if function has no @workflow.atom(...) decorator."""
        return not any(
            isinstance(deco, ast.Call) and getattr(deco.func, 'attr', None) == 'atom'
            for deco in node.decorator_list
        )

    def _is_user_defined_blackbox_function(self, node: ast.FunctionDef) -> bool:
        """
        Return True if the user-defined function should be treated as a blackbox helper.

        This is true in two cases:
        1. It is explicitly called from top-level user code (and not @decorated)
        2. It has parameters AND does not contain any known component calls or known atom usage

        We never apply this to explicitly decorated @workflow.atom functions.
        """
        if not self._is_undecorated(node):
            return False  # explicitly decorated, always keep

        if node.name in self._top_level_user_function_calls:
            return True  # called manually by user script

        if node.args.args and not (
            self._uses_known_atoms(node) or self._contains_known_component_call(node)
        ):
            return True  # parametric helper function with no reactive behavior

        return False

    def _is_blackbox_call(self, stmt: ast.stmt) -> bool:
        if not hasattr(stmt, "value") or not isinstance(stmt.value, ast.Call):
            return False
        func = stmt.value.func
        return (
            isinstance(func, ast.Name)
            and any(fn.name == func.id for fn in self._all_function_defs)
            and not self._should_inline_function(func.id)
        )

    def _is_expr_blackbox_call(self, stmt: ast.Expr) -> bool:
        call_node = stmt.value
        return (
            isinstance(call_node, ast.Call)
            and isinstance(call_node.func, ast.Name)
            and any(fn.name == call_node.func.id for fn in self._all_function_defs)
            and not self._should_inline_function(call_node.func.id)
        )

    def _collect_top_level_user_calls(self, body: list[ast.stmt]) -> set[str]:
        called_funcs = set()

        for stmt in body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name):
                    called_funcs.add(stmt.value.func.id)
            elif isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name):
                    called_funcs.add(stmt.value.func.id)

        return called_funcs

    def _lift_augassign_stmt(self, stmt: ast.AugAssign) -> None:
        """
        Lifts an augmented assignment statement (e.g. `counter += val`) into a reactive atom function.

        The resulting atom recomputes the updated value based on both the left-hand side (LHS)
        and right-hand side (RHS) expressions, resolving dependency mappings automatically.

        The generated atom function is appended to `self.generated_atoms` for later injection
        into the transformed AST.

        Args:
            stmt: The original `ast.AugAssign` statement to lift.

        Returns:
            None
        """
        class DependencyReplacer(ast.NodeTransformer):
            def visit_Name(self, node): # noqa: N802
                if isinstance(node.ctx, ast.Load) and node.id in scoped_map:
                    atom = scoped_map[node.id]
                    mapped = param_mapping.get(atom)
                    if mapped:
                        return ast.Name(id=mapped, ctx=ast.Load())
                return node

        scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        target = stmt.target

        if not isinstance(target, ast.Name):
            register_error(
                type="ast_transform",
                filename=self.filename,
                lineno=self._get_stable_lineno(stmt, "augassign"),
                message="Only simple variable names are supported as targets for augmented assignment.",
                source=ast.unparse(stmt),
                component_id=None,
                atom_name=None,
            )
            logger.error("[AST] AugAssign target is not a simple name")
            return

        callsite_deps, dep_names = self._find_unique_dependencies(stmt.value, scoped_map)

        # Ensure the LHS variable is included as a dependency
        lhs_atom = scoped_map.get(target.id)
        if lhs_atom and lhs_atom not in callsite_deps:
            callsite_deps.insert(0, lhs_atom)
            dep_names.insert(0, target.id)

        component_id, atom_name = self.generate_component_and_atom_name("producer", stmt)
        param_mapping = self._make_param_mapping(callsite_deps)

        # Create the equivalent `Assign` node for the augmented expression (e.g. `counter = counter + val`)
        lhs_expr = ast.Name(id=param_mapping.get(lhs_atom, target.id), ctx=ast.Load())
        rhs_expr = DependencyReplacer().visit(copy.deepcopy(stmt.value))
        bin_expr = ast.BinOp(left=lhs_expr, op=stmt.op, right=rhs_expr)

        assign_stmt = ast.Assign(
            targets=[ast.Name(id=target.id, ctx=ast.Store())],
            value=bin_expr
        )

        # Register variable binding and lift the new assign into an atom
        self._register_variable_bindings(assign_stmt, atom_name)
        self._current_frame.variable_to_atom[target.id] = atom_name
        self._finalize_and_register_atom(
            atom_name,
            component_id,
            callsite_deps,
            assign_stmt,
            return_target=ast.Name(id=target.id, ctx=ast.Load())
        )

    def _lift_output_stream_stmt(self, stmt: ast.Expr, component_id: str, atom_name: str, stream: str) -> None:
        """
        Lifts a function call that writes to a stream (like print()) into a reactive atom function.
        After execution, the stream's contents can be captured and rendered as output.
        """
        scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        callsite_deps, dep_names = self._find_unique_dependencies(stmt.value, scoped_map)

        param_mapping = self._make_param_mapping(callsite_deps)
        patched_expr = self._replace_dep_args(stmt.value, param_mapping)

        patched_expr_code = ''
        try:
            patched_expr_code = ast.unparse(patched_expr)
        except Exception as e:
            self._safe_register_error(
                node=patched_expr,
                lineno=self._get_stable_lineno(stmt, "print(...)"),
                message="Could not unparse stream expression",
                component_id=component_id,
                atom_name=atom_name,
                extra_context="Output stream lifting",
            )
            logger.error(f"[AST] Unparsing failed in output stream lift: {e}")
            return

        source = textwrap.dedent(f"""
            from contextlib import redirect_stdout
            from io import StringIO
            from preswald.interfaces.render.registry import build_component_return_from_value
            _stdout_capture = StringIO()
            with redirect_stdout(_stdout_capture):
                {patched_expr_code}
            _stdout_value = _stdout_capture.getvalue()
            stdout_value = _stdout_capture.getvalue()
            return build_component_return_from_value(stdout_value, mimetype="text/plain", component_id="{component_id}")
        """)

        try:
            call_and_return = ast.parse(source).body
            self._finalize_and_register_atom(atom_name, component_id, callsite_deps, call_and_return)
        except SyntaxError as e:
            self._safe_register_error(
                lineno=self._get_stable_lineno(stmt, "output stream code generation"),
                message=f"Failed to parse generated code: {e}",
                fallback_source=source,
                component_id=component_id,
                atom_name=atom_name,
                extra_context="Output stream code generation failure",
            )
            logger.error(f"[AST] Generated code could not be parsed: {e}")
            return

    def _lift_return_renderable_call(
        self,
        stmt: ast.stmt,
        call_node: ast.Call,
        component_id: str,
        atom_name: str,
        mimetype: str,
    ) -> None:
        """
        Lifts a call like `df.head()` into an atom and wraps the result using `build_component_return_from_value`.

        Args:
            stmt: The original AST statement (Expr or Assign).
            call_node: The ast.Call representing the df.head() or similar.
            component_id: Stable component ID for frontend reconciliation.
            atom_name: Unique atom name for the function.
            mimetype: MIME type of the rendered output (e.g. "text/html")
        """
        scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        callsite_deps, dep_names = self._find_unique_dependencies(
            call_node,
            scoped_map,
            stmt=stmt,
            component_id=component_id,
            atom_name=atom_name,
            context="return_renderable_call"
        )

        param_mapping = self._make_param_mapping(callsite_deps)
        call_expr = self._replace_dep_args(call_node, param_mapping, scoped_map)

        wrapped_call = ast.Call(
            func=ast.Name(id="build_component_return_from_value", ctx=ast.Load()),
            args=[call_expr],
            keywords=[
                ast.keyword(arg="mimetype", value=ast.Constant(value=mimetype)),
                ast.keyword(arg="component_id", value=ast.Constant(value=component_id)),
            ]
        )

        self._finalize_and_register_atom(atom_name, component_id, callsite_deps, wrapped_call)

    def _lift_side_effect_stmt(self, stmt: ast.Expr) -> None:
        """
        Lifts a method call that causes a side effect into a reactive atom.

        This is used when an expression produces side effects and depends on one or more reactive variables.
        The resulting atom will rerun whenever any of its dependencies change, ensuring side effects are re-applied.

        Example:
            fig, ax = plt.subplots()
            ax.plot([0, 1, 2], [n**2, (n+1)**2, (n+2)**2])  # This gets lifted into an atom depending on both ax and n

        Supported patterns:
        - Method calls such as `obj.method(...)` where `obj` or arguments are reactive
        - Tuple returning atoms and param mapping are fully supported
        - Only direct variable references (`ast.Name`) are rewritten; complex expressions are passed through as is

        This function:
        - Locates all dependency variables from the method call
        - Constructs a reactive atom that re-invokes the method on change
        - Registers the atom with correctly mapped parameters for replaying the side effect

        Args:
            stmt: An `ast.Expr` node representing the top level method call.

        Returns:
            None. The generated atom is registered internally.
        """

        receiver = stmt.value.func.value
        if not isinstance(receiver, ast.Name):
            self._safe_register_error(
                node=stmt,
                message="Side effect call not lifted: receiver is not a simple variable reference.",
                extra_context="Expected receiver to be ast.Name",
            )
            return

        scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        callsite_deps, dep_names = self._find_unique_dependencies(
            stmt.value,
            variable_map=scoped_map,
            stmt=stmt,
            context="side_effect_call"
        )
        if not callsite_deps:
            return

        try:
            atom_to_vars = defaultdict(list)
            for var in dep_names:
                atom_to_vars[scoped_map[var]].append(var)

            reverse_map = {}
            for i, atom in enumerate(callsite_deps):
                param_name = f"param{i}"
                for var in atom_to_vars[atom]:
                    if atom not in self._current_frame.tuple_returning_atoms:
                        reverse_map[var] = ast.Name(id=param_name, ctx=ast.Load())
                    else:
                        index = self._current_frame.tuple_variable_index.get(var)
                        if index is not None:
                            reverse_map[var] = ast.Subscript(
                                value=ast.Name(id=param_name, ctx=ast.Load()),
                                slice=ast.Constant(value=index),
                                ctx=ast.Load(),
                            )

            class Replacer(ast.NodeTransformer):
                def visit_Name(self, node: ast.Name):
                    return reverse_map.get(node.id, node)

            patched_call = Replacer().visit(copy.deepcopy(stmt.value))
            ast.fix_missing_locations(patched_call)

            component_id, atom_name = self.generate_component_and_atom_name("sideeffect", stmt)
            atom_body = [ast.Expr(value=patched_call)]
            self._finalize_and_register_atom(atom_name, component_id, callsite_deps, atom_body)
            logger.debug('[AST] lifted side effect statement into atom %s -> %s', component_id, atom_name)

        except Exception as e:
            self._safe_register_error(
                node=stmt,
                message=f"Failed to lift side effect call: {e}",
                extra_context="AST rewrite or registration failure",
            )

    def _lift_blackbox_function_call(
        self,
        stmt: ast.stmt,
        func_name: str,
        scoped_map: dict[str, str],
        variable_map: dict[str, str],
    ) -> None:
        logger.debug('[DEBUG] enter _lift_blackbox_function_call')

        component_id, atom_name = self.generate_component_and_atom_name(func_name, stmt)

        call_expr = getattr(stmt, "value", None)
        if not isinstance(call_expr, ast.Call):
            self._safe_register_error(
                node=stmt,
                message="Expected function call expression in blackbox lifting.",
                component_id=component_id,
                atom_name=atom_name,
            )
            return

        callsite_deps, dep_names = self._find_unique_dependencies(call_expr, scoped_map)
        param_mapping = self._make_param_mapping(callsite_deps)
        self._blackbox_lifted_functions.add(func_name)

        # Build: __preswald_result__ = blackbox(param0, ...)
        try:
            replaced_call = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[ast.Name(id=param_mapping[dep], ctx=ast.Load()) for dep in callsite_deps],
                keywords=[]
            )
        except KeyError as e:
            self._safe_register_error(
                node=stmt,
                message=f"Failed to lift blackbox function call: unknown dependency {e}",
                component_id=component_id,
                atom_name=atom_name,
            )
            return

        temp_assign = ast.Assign(
            targets=[ast.Name(id="__preswald_result__", ctx=ast.Store())],
            value=replaced_call
        )

        # Handle lhs target or inline call
        if isinstance(stmt, ast.Assign):
            lhs = stmt.targets[0]

            if isinstance(lhs, ast.Tuple | ast.List):
                self._current_frame.tuple_returning_atoms.add(atom_name)

                for index, elt in enumerate(lhs.elts):
                    if isinstance(elt, ast.Name):
                        var = elt.id
                        variable_map[var] = atom_name
                        self._current_frame.tuple_variable_index[var] = index

                return_targets = [elt.id for elt in lhs.elts if isinstance(elt, ast.Name)]
                return_target = return_targets if len(return_targets) > 1 else (return_targets[0] if return_targets else None)

                unpack_assign = ast.Assign(
                    targets=[lhs],
                    value=ast.Name(id="__preswald_result__", ctx=ast.Load())
                )

                body = [temp_assign, unpack_assign]

            elif isinstance(lhs, ast.Name):
                variable_map[lhs.id] = atom_name
                return_target = "__preswald_result__"
                body = [temp_assign]
            else:
                self._safe_register_error(
                    node=stmt,
                    message="Unsupported left-hand side for blackbox function call.",
                    component_id=component_id,
                    atom_name=atom_name,
                )
                return

            self._current_frame.variable_to_atom.update(variable_map)

        elif isinstance(stmt, ast.Expr):
            return_target = "__preswald_result__"
            body = [temp_assign]

        else:
            self._safe_register_error(
                node=stmt,
                message="Unsupported statement type for blackbox function call.",
                component_id=component_id,
                atom_name=atom_name,
            )
            return

        logger.debug(f'[DEBUG] _lift_blackbox_function_call {component_id=}; {atom_name=}; {dep_names=}')
        self._finalize_and_register_atom(
            atom_name,
            component_id,
            callsite_deps,
            body,
            return_target=return_target
        )

    def _lift_producer_stmt(self, stmt: ast.Assign, pending_assignments: list[ast.Assign], variable_map: dict[str, str]) -> None:
        """
        Lifts a producer assignment statement into a reactive atom function. A producer statement is any
        variable assignment with a computed value.

        This handles two types of producer statements:
          1. Single assignment: `x = val * 2`
          2. Tuple unpacking: `a, b = my_func(x)`

        For each case, the lifted code:
          - Extracts dependencies from the RHS expression(s)
          - Maps dependencies to function parameters
          - Constructs an atom function with a `@workflow.atom` decorator
          - Registers new variable-to-atom bindings
          - Appends the atom to `self.generated_atoms` for later injection into the AST

        Limitations:
          - Only supports assignment targets that are `ast.Name` nodes. This excludes:
              * Attribute assignments: `obj.attr = ...`
              * Subscript assignments: `data['key'] = ...`
              * Starred unpacking: `a, *rest = ...`
          - Tuple and list unpacking is supported only for flat `a, b = ...` or `[a, b] = ...` patterns.

        Args:
            stmt: An `ast.Assign` node representing the assignment to lift.
            pending_assignments: Not currently used, reserved for deferred handling of delayed expressions.
            variable_map: The current scoped variable-to-atom mapping.
        """
        result_var = "__preswald_result__"
        scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}

        logger.debug(f"[AST] About to lift producer: {ast.dump(stmt)}")
        logger.debug(f"[AST] scoped_map={scoped_map}")

        return_target: str | list[str] | None = None
        if isinstance(stmt.targets[0], ast.Tuple | ast.List):
            component_id, atom_name = self.generate_component_and_atom_name("producer")
            self._current_frame.tuple_returning_atoms.add(atom_name)

            unpacked_vars = [
                elt.id for elt in stmt.targets[0].elts
                if isinstance(elt, ast.Name)
            ]
            self._current_frame.tuple_unpacked_names[atom_name] = unpacked_vars

            # Attempt to infer return type for the leftmost variable (assumed to be the primary return object)
            if isinstance(stmt.value, ast.Call):
                self._infer_and_register_return_type(stmt.value, atom_name)

            temp_assign = ast.Assign(
                targets=[ast.Name(id=result_var, ctx=ast.Store())],
                value=stmt.value
            )

            unpack_assign = ast.Assign(
                targets=[ast.Tuple(
                    elts=[
                        ast.Name(id=elt.id, ctx=ast.Store())
                        for elt in stmt.targets[0].elts
                        if isinstance(elt, ast.Name)
                    ],
                    ctx=ast.Store()
                )],
                value=ast.Name(id=result_var, ctx=ast.Load())
            )

            return_targets = [
                elt.id for elt in stmt.targets[0].elts
                if isinstance(elt, ast.Name)
            ]
            return_target = return_targets if len(return_targets) > 1 else (return_targets[0] if return_targets else None)

            body = [temp_assign, unpack_assign]
            callsite_deps, dep_names = self._find_unique_dependencies(
                ast.Module(body=body, type_ignores=[]),
                scoped_map,
                stmt=stmt,
                component_id=component_id,
                atom_name=atom_name,
                context="tuple_unpacking"
            )

            param_mapping = self._make_param_mapping(callsite_deps)
            patched_expr = [
                ast.Assign(
                    targets=[ast.Name(id=result_var, ctx=ast.Store())],
                    value=self._replace_dep_args(stmt.value, param_mapping)
                ),
                unpack_assign
            ]

            logger.info(f"[AST] Lifted tuple unpacking producer: {atom_name=} {callsite_deps=}")

            for index, elt in enumerate(stmt.targets[0].elts):
                if isinstance(elt, ast.Name):
                    var = elt.id
                    logger.debug(f"[AST] tuple unpacking: {var=} index={index} atom={atom_name}")
                    variable_map[var] = atom_name # ensures that while generating the function body (especially patched_expr in consumers), the variables get correctly replaced.
                    self._current_frame.variable_to_atom[var] = atom_name # ensures future _uses_known_atoms and _find_dependencies see this binding.
                    self._current_frame.tuple_variable_index[var] = index # tells the transformer where in the returned tuple each variable sits

        elif isinstance(stmt.targets[0], ast.Subscript):
            # Extract base variable from the original target before replacement
            original_target = stmt.targets[0]
            if not isinstance(original_target.value, ast.Name):
                self._safe_register_error(
                    node=stmt,
                    message="Unsupported subscript assignment pattern (must be like `x[i] = ...`).",
                    component_id=None,
                    atom_name=None,
                )
                return

            mutated_var = original_target.value.id
            mutated_atom = self._current_frame.variable_to_atom.get(mutated_var)
            if not mutated_atom:
                self._safe_register_error(
                    node=stmt,
                    message=f"Cannot lift subscript assignment: `{mutated_var}` is not tracked as a reactive variable.",
                    component_id=None,
                    atom_name=None,
                )
                logger.error(
                    "[AST] Cannot lift subscript assignment: `%s` is not reactive. variable_map keys=%s, current reactive keys=%s",
                    mutated_var,
                    list(variable_map.keys()),
                    list(self._current_frame.variable_to_atom.keys())
                )
                return

            component_id, new_atom_name = self.generate_component_and_atom_name("subassign", stmt)
            # Use current reactive scope as fallback variable map
            variable_map = self._current_frame.variable_to_atom
            rhs_deps, _ = self._find_unique_dependencies(
                stmt.value,
                variable_map,
                stmt=stmt,
                component_id=component_id,
                atom_name=new_atom_name,
                context="subscript_assignment"
            )

            deps = [mutated_atom] + [d for d in rhs_deps if d != mutated_atom]
            param_mapping = self._make_param_mapping(deps)

            patched_stmt = ast.Assign(
                targets=[self._replace_dep_args(original_target, param_mapping)],
                value=self._replace_dep_args(stmt.value, param_mapping),
            )

            return_param = param_mapping[mutated_atom]
            return_target = ast.Name(id=return_param, ctx=ast.Load())

            self._finalize_and_register_atom(
                new_atom_name,
                component_id,
                deps,
                [patched_stmt],
                return_target=return_target
            )
            logger.info("[AST] lifted subscript assignment into atom %s -> %s", component_id, new_atom_name)
            return
        else:
            component_id, atom_name = self.generate_component_and_atom_name("producer", stmt)
            callsite_deps, dep_names = self._find_unique_dependencies(
                stmt.value,
                scoped_map,
                stmt=stmt,
                component_id=component_id,
                atom_name=atom_name,
                context="single_assignment"
            )

            # Track the return type if this is a call to a known constructor
            # this is so that we can use this type to lookup registered renderables and lift them
            if isinstance(stmt.value, ast.Call):
                self._infer_and_register_return_type(stmt.value, atom_name)

            param_mapping = self._make_param_mapping(callsite_deps)
            patched_expr = ast.Assign(
                targets=stmt.targets,
                value=self._replace_dep_args(stmt.value, param_mapping, scoped_map)
            )

            return_targets = []
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    variable_map[target.id] = atom_name
                    return_targets.append(target.id)

            if len(return_targets) == 1:
                return_target = return_targets[0]
            elif return_targets:
                return_target = return_targets

            self._register_variable_bindings(stmt, atom_name)
            logger.debug(f"[AST] Lifted producer: {atom_name=} {callsite_deps=}")

        self._finalize_and_register_atom(atom_name, component_id, callsite_deps, patched_expr, return_target=return_target)
        self._current_frame.variable_to_atom.update(variable_map)

    def _lift_consumer_stmt(self, stmt: ast.Expr, *, component_id: str | None = None, atom_name: str | None = None) -> ast.Expr:
        """
        Lifts a consumer expression statement (e.g. `text(f"Hi {x}")`) into a reactive atom function.

        Consumer expressions are side-effect-producing calls (typically to UI components) that depend
        on reactive inputs and must rerun when their inputs change. This function rewrites those
        expressions into parametrized atom functions that re-execute only when dependencies change.

        The lifted atom is appended to `self.generated_atoms`, and the original expression is
        replaced with a callsite to the generated atom.

        This function also handles:
          - Tuple-returning atoms via index-based access (`param[i]`)
          - Reverse mapping of dependency variables to param expressions

        Args:
            stmt: An `ast.Expr` node representing a top-level expression statement.

        Returns:
            A new `ast.Expr` with the value replaced by a call to the generated atom function.
        """
        class TupleAwareReplacer(ast.NodeTransformer):
            def visit_Name(self, node: ast.Name): # noqa: N802
                if isinstance(node.ctx, ast.Load) and node.id in reverse_map:
                    return reverse_map[node.id]
                return node


        scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        expr = stmt.value
        callsite_deps, dep_names = self._find_unique_dependencies(
            expr,
            scoped_map,
            stmt=stmt,
            component_id=component_id,
            atom_name=atom_name,
            context="consumer_stmt"
        )

        component_id, atom_name = (
            (component_id, atom_name)
            if component_id and atom_name
            else self.generate_component_and_atom_name("consumer", stmt)
        )

        # Group variables by originating atom
        atom_to_vars: dict[str, list[str]] = defaultdict(list)
        for var in dep_names:
            atom_to_vars[scoped_map[var]].append(var)

        # Build reverse lookup from variable -> parameter expression
        reverse_map: dict[str, ast.expr] = {}
        for i, atom in enumerate(callsite_deps):
            param_name = f"param{i}"
            for var in atom_to_vars[atom]:
                if atom not in self._current_frame.tuple_returning_atoms:
                    reverse_map[var] = ast.Name(id=param_name, ctx=ast.Load())
                else:
                    index = self._current_frame.tuple_variable_index.get(var)
                    if index is not None:
                        reverse_map[var] = ast.Subscript(
                            value=ast.Name(id=param_name, ctx=ast.Load()),
                            slice=ast.Constant(value=index),
                            ctx=ast.Load()
                        )
                    else:
                        self._safe_register_error(
                            node=stmt,
                            message=f"Tuple-returning atom is missing an index for variable '{var}' from atom '{atom}'",
                            component_id=component_id,
                            atom_name=atom_name,
                        )
                        logger.warning(f"[AST] Missing tuple index for var={var} from atom={atom}")

        patched_expr = TupleAwareReplacer().visit(copy.deepcopy(expr))
        ast.fix_missing_locations(patched_expr)

        self._finalize_and_register_atom(atom_name, component_id, callsite_deps, patched_expr)

        # Return the rewritten expression as a call to the generated atom
        callsite = self._make_callsite(atom_name, callsite_deps)
        return ast.Expr(value=callsite)

    def _resolve_display_return_type(self, atom_name: str, varname: str) -> str | None:
        types = self._current_frame.atom_return_types.get(atom_name)
        if types is None:
            return None
        if isinstance(types, tuple):
            unpacked = self._current_frame.tuple_unpacked_names.get(atom_name, [])
            if varname not in unpacked:
                return None
            index = unpacked.index(varname)
            return types[index]
        return types

    def _try_lift_display_renderer(
            self, *, candidate: str, stmt: ast.stmt, component_id: str | None = None, dependencies: list[str] | None = None
        ) -> bool:
        """
        Attempts to lift a display renderer call into a reactive atom.

        This function checks whether a registered display renderer matches the given candidate,
        and if so, generates a new atom that calls the renderer function with the appropriate
        dependencies. It ensures correct parameter mapping, handles tuple returning atoms,
        and injects the atom into the runtime.

        Args:
            candidate: The string key identifying a registered display renderer.
            stmt: The AST statement containing the call to lift.
            component_id: Optional preset component ID. If not provided, one is generated.
            dependencies: Optional list of atom dependencies. If not provided, they are inferred.

        Returns:
            True if lifting succeeded and the atom was registered, False otherwise.
        """
        logger.debug(f"[DEBUG] Attempting to lift display renderer: {candidate=}, {component_id=}, {dependencies=}")

        renderer_fn = get_display_renderers().get(candidate)
        if not renderer_fn:
            logger.warning(f"[DEBUG] No renderer function registered for: {candidate}")
            return False

        self._used_display_renderer_fns.add(renderer_fn.__name__)

        if component_id is None:
            component_id, atom_name = self.generate_component_and_atom_name(candidate, stmt)
        else:
            atom_name = generate_stable_atom_name_from_component_id(component_id)

        logger.debug(f'[DEBUG] in _try_lift_display_renderer component id and atom name generated for {renderer_fn.__name__=} {component_id=} {atom_name=}')

        call_node = stmt.value if isinstance(stmt, ast.Expr) else stmt.value if isinstance(stmt, ast.Assign) else None
        if not isinstance(call_node, ast.Call):
            logger.warning(f"[DEBUG] Statement does not contain a valid call: {stmt}")
            return False

        # Inspect the renderer function to determine parameter names
        sig = inspect.signature(renderer_fn)
        expected_params = [p for p in sig.parameters.values() if p.name != "component_id"]

        #variable_map = self._get_variable_map_for_stmt(stmt)
        variable_map = self._current_frame.variable_to_atom

        receiver_node = getattr(call_node.func, "value", None)
        callsite_deps = dependencies
        if not callsite_deps:
            callsite_deps, dep_names = (
                self._find_unique_dependencies(
                    receiver_node,
                    variable_map,
                    stmt=stmt,
                    component_id=component_id,
                    atom_name=atom_name,
                    context=f"display_renderer: {candidate}"
                )
                if receiver_node else ([], [])
            )

        if len(callsite_deps) < len(expected_params):
            self._safe_register_error(
                node=stmt,
                message=f"Insufficient dependencies extracted for display renderer `{candidate}`.",
                component_id=component_id,
                atom_name=atom_name,
                extra_context=f"Expected {len(expected_params)} but got {len(callsite_deps)}",
            )
            return False

        renderer_args = []
        for i, param in enumerate(expected_params):
            dep_atom = callsite_deps[i]
            if dep_atom in self._current_frame.tuple_returning_atoms:
                arg_expr = ast.Subscript(
                    value=ast.Name(id=f"param{i}", ctx=ast.Load()),
                    slice=ast.Constant(value=0),
                    ctx=ast.Load(),
                )
                renderer_args.append(arg_expr)
                logger.debug(f"[LIFT] Injected subscripted tuple arg: param{i}[0] for {param.name=}")
            else:
                renderer_args.append(ast.Name(id=f"param{i}", ctx=ast.Load()))
                logger.debug(f"[LIFT] Injected standard arg: param{i} for {param.name=}")

        # Build renderer(fig, component_id=...)
        renderer_call = ast.Call(
            func=ast.Name(id=renderer_fn.__name__, ctx=ast.Load()),
            args=renderer_args,
            keywords=[
                ast.keyword(arg="component_id", value=ast.Constant(value=component_id))
            ],
        )

        self._finalize_and_register_atom(atom_name, component_id, callsite_deps, renderer_call)

        #logger.debug(f"[DEBUG] Replacing .show call with call to: {renderer_fn.__name__}({object_arg=}, {component_id=})")

        return True

    def _maybe_lift_display_renderer_from_expr(self, stmt: ast.Expr, call_node: ast.Call) -> bool:
        logger.debug(f'[DEBUG] _maybe_lift_display_renderer_from_expr - {stmt=}; {call_node=}')
        if not isinstance(call_node.func, ast.Attribute):
            logger.debug('[DEBUG] _maybe_lift_display_renderer_from_expr - returning because call_node.func is not an instance of attribute')
            return False

        attr = call_node.func.attr
        receiver = call_node.func.value
        varname = None

        if isinstance(receiver, ast.Name):
            varname = receiver.id
        elif isinstance(receiver, ast.Subscript) and isinstance(receiver.value, ast.Name):
            varname = receiver.value.id
        else:
            logger.debug(f'[DEBUG] _maybe_lift_display_renderer_from_expr - returning receiver is not a Name or Subscript {receiver=}')

            return False

        logger.debug(f'[DEBUG] _maybe_lift_display_renderer_from_expr - {receiver=}; {attr=}; {varname=}')

        atom_name = self._current_frame.variable_to_atom.get(varname)
        return_type = self._resolve_display_return_type(atom_name, varname)

        # TODO: we used to try display methods here, but the logic was incomplete. Determine if we would like to add support back for display_methods. Do we have a strong use case for this functionality?

        if return_type:
            candidate = f"{return_type}.{attr}"
            logger.debug(f"[registry] resolved display renderer candidate from return type: {candidate}")
        else:
            fallback_base = self._variable_class_map.get(varname) or self.import_aliases.get(varname, varname)
            candidate = f"{fallback_base}.{attr}"
            logger.debug(f"[registry] resolved fallback display renderer candidate: {candidate}")

        renderer = get_display_renderers().get(candidate)
        if renderer:
            atom_name = self._current_frame.variable_to_atom.get(varname)
            if atom_name:
                return self._try_lift_display_renderer(candidate=candidate, stmt=stmt, dependencies=[atom_name])
            else:
                logger.warning(f"[AST] Display renderer fallback: unknown dependency for varname={varname}")

        # check detectors
        for detector in get_display_detectors():
            logger.debug(f'[DEBUG] _maybe_lift_display_renderer_from_expr - applying detector to {call_node=}')
            if detector(call_node):
                candidate = f"{self.import_aliases.get(varname, varname)}.{attr}"
                resolver = get_display_dependency_resolvers().get(candidate)
                deps = resolver(self._current_frame) if resolver else []
                logger.debug(f'[DEBUG] _maybe_lift_display_renderer_from_expr - detected candidate {resolver=}; {candidate=}; {stmt=}; {deps=}')
                return self._try_lift_display_renderer(candidate=candidate, stmt=stmt, dependencies=deps)

        logger.debug(f'[DEBUG] _maybe_lift_display_renderer_from_expr - nothing handled, returning False {candidate=}')

        return False

    def _lift_statements( # noqa: C901
        self,
        body: list[ast.stmt],
        component_metadata: dict[int, tuple[str, str]] | None = None,
    ) -> list[ast.stmt]:
        """
        Second pass over the module body to lift top-level reactive statements into atoms.

        This includes:
          - Known component calls lifted via metadata
          - Consumer expressions that depend on reactive variables
          - Producer assignments with reactive dependencies: `x = val * 2`
          - Augmented assignments (`x += val`) when reactive values are involved

        Non-reactive assignments and expressions are preserved in the returned `new_body`.

        Args:
            body: Original top level statements from the module.
            component_metadata: Mapping from AST call node ID to (component_id, atom_name).

        Returns:
            A list of top level statements that are not lifted, to include in the rewritten module.
        """
        logger.debug(f"[DEBUG] Lifting statements inside function: {self.current_function.name if self.current_function else '<module>'}")
        logger.debug(f"[DEBUG] _lift_statements in {self.current_function.name if self.current_function else '<module>'}")

        component_metadata = component_metadata or {}
        return_renderers = {} if self._in_function_body else get_return_renderers()
        output_stream_calls = {} if self._in_function_body else get_output_stream_calls()
        display_methods = {} if self._in_function_body else get_display_methods()

        stmt_variable_maps, _ = self._generate_stmt_variable_maps(body, component_metadata)

        logger.debug(f'[DEBUG] {return_renderers=} {output_stream_calls}')

        new_body = []
        pending_assignments = []

        for stmt in body:
            # Skip imports as they are handled separately
            if isinstance(stmt, ast.Import | ast.ImportFrom):
                continue

            # skip user defined functions unless they are explicitly decorated or contain reactive calls
            if isinstance(stmt, ast.FunctionDef):
                if self._is_undecorated(stmt) and self._is_user_defined_blackbox_function(stmt):
                    logger.debug(f"[DEBUG] Skipping non-reactive user function: {stmt.name}")
                    new_body.append(stmt)
                    continue

            scoped_map = {**self._current_frame.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
            variable_map = stmt_variable_maps.get(stmt, {})

            if isinstance(stmt, ast.Expr) and self._is_expr_blackbox_call(stmt):
                logger.debug(f"[AST] Falling back to blackbox lifting for expression: {stmt.value.func.id}")
                self._lift_blackbox_function_call(stmt, stmt.value.func.id, scoped_map, variable_map)
                continue

            logger.debug(f"[DEBUG] variable_map for stmt: {stmt} -> {stmt_variable_maps.get(stmt)}")
            logger.debug(f"[DEBUG] Examining stmt: {ast.dump(stmt)}")

            # Handle in script resolver registrations, such as register_display_dependency_resolver
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name)
                and len(stmt.value.args) == 2
                and isinstance(stmt.value.args[0], ast.Constant)
            ):
                if (stmt.value.func.id == "register_display_dependency_resolver"):
                    func_name_node = stmt.value.args[0]
                    resolver_node = stmt.value.args[1]

                    # Validate argument type before attempting compilation
                    if not isinstance(resolver_node, ast.Lambda):
                        source_text = ast.unparse(stmt)
                        lineno = self._get_stable_lineno(stmt.value, "register_display_dependency_resolver")

                        register_error(
                            type="ast_transform",
                            filename=self.filename,
                            lineno=lineno,
                            message="Second argument to register_display_dependency_resolver must be a lambda expression.",
                            source=source_text,
                            component_id=None,
                            atom_name=None,
                        )

                        logger.warning("[AST] register_display_dependency_resolver: expected lambda as second argument")
                        continue

                    logger.info('[DEBUG] inside register_display_dependency_resolver gaurd')

                    try:
                        func_name = func_name_node.value  # e.g. "matplotlib.pyplot.show"
                        lambda_code = ast.Expression(body=resolver_node)
                        compiled = compile(lambda_code, filename="<resolver>", mode="eval")
                        resolver_fn = eval(compiled, {"__builtins__": __builtins__})  # only eval the lambda
                        register_display_dependency_resolver(func_name, resolver_fn)  # then call actual registrar
                        logger.debug(f"[AST] Registered display dependency resolver for {func_name=}")
                    except Exception as e:
                        source_text = ast.unparse(stmt)
                        lineno = self._get_stable_lineno(stmt.value, "register_display_dependency_resolver")
                        register_error(
                            type="ast_transform",
                            filename=self.filename,
                            lineno=lineno,
                            message=str(e),
                            source=source_text,
                            component_id=None,
                            atom_name=None,
                        )
                        logger.warning(f"[AST] Failed to register resolver: {e}")

                    continue

            call_node = None
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value

            # Handle known component calls via metadata
            if call_node:
                logger.debug(f'handing known compnent calls {display_methods.items()=}')
                if self._is_known_component_call(call_node):
                    full_func_name = self._get_call_func_name(call_node)
                    logger.debug(f"[DEBUG] Attempting to lift known component call '{full_func_name}' inside {self.current_function.name if self.current_function else '<module>'}")
                    component_id, atom_name = component_metadata.get(id(call_node), (None, None))

                    if not atom_name:
                        # Fallback path in case metadata was not precomputed
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"[AST] Missing atom mapping for {full_func_name=}. Regenerating...")
                        component_id, atom_name = self.generate_component_and_atom_name(full_func_name, stmt)

                    if self._uses_known_atoms(stmt):
                        self._lift_consumer_stmt(stmt)
                    else:
                        self.lift_component_call_to_atom(call_node, component_id, atom_name, variable_map)

                    continue

                # handle return renderables
                if isinstance(call_node.func, ast.Attribute):
                    attr = call_node.func.attr
                    receiver = call_node.func.value
                    if isinstance(receiver, ast.Name):
                        varname = receiver.id
                        full_func_name = f"{varname}.{attr}"

                        if full_func_name in return_renderers:
                            mimetype = return_renderers[full_func_name]["mimetype"]
                            logger.debug(f"[AST] Lifting return-renderable: {full_func_name=}; {mimetype=}")
                            component_id, atom_name = self.generate_component_and_atom_name(full_func_name, stmt)
                            self._lift_return_renderable_call(stmt, call_node, component_id, atom_name, mimetype)
                            continue

                if isinstance(call_node.func, ast.Name):
                    func_name = call_node.func.id

                    # Detect stream-based function (like print)
                    if func_name in output_stream_calls:
                        component_id, atom_name = self.generate_component_and_atom_name(func_name, stmt)
                        self._lift_output_stream_stmt(stmt, component_id, atom_name, stream=output_stream_calls[func_name])
                        continue

                logger.debug(f"[AST] Checking attribute call for return-renderable: {ast.dump(call_node.func)}")

                logger.debug(f"[AST] import_aliases={self.import_aliases}")

                # Handle return-renderable method based on inferred variable type
                if isinstance(call_node.func, ast.Attribute) and isinstance(call_node.func.value, ast.Name):
                    varname = call_node.func.value.id  # e.g. param0
                    attr = call_node.func.attr         # e.g. to_html

                    atom_name = self._current_frame.variable_to_atom.get(varname)
                    logger.debug(f"[AST] Lookup for variable: {varname=} -> {atom_name=}")
                    if atom_name:
                        return_type = self._current_frame.atom_return_types.get(atom_name)
                        if return_type:
                            canonical_type = self.import_aliases.get(return_type, return_type)
                            candidate = f"{canonical_type}.{attr}"  # e.g. pandas.DataFrame.to_html

                            # normalize candidate from import aliases
                            if '.' in candidate:
                                prefix, suffix = candidate.split('.', 1)
                                prefix = self.import_aliases.get(prefix, prefix)
                                candidate = f"{prefix}.{suffix}"

                            logger.debug(f"[AST] Trying candidate: {candidate=}, available renderers: {list(return_renderers.keys())}")

                            if candidate in return_renderers:
                                mimetype = return_renderers[candidate]["mimetype"]
                                logger.debug(f"[AST] Lifting return-renderable by type: {candidate=}; {mimetype=}")
                                component_id, atom_name = self.generate_component_and_atom_name(candidate, stmt)
                                self._lift_return_renderable_call(stmt, call_node, component_id, atom_name, mimetype)
                                continue

            # Handle expression consumers and side effects
            if isinstance(stmt, ast.Expr):

                # case 1: display renderers ( must be first )
                if isinstance(stmt.value, ast.Call):
                    call_node = stmt.value
                    if self._maybe_lift_display_renderer_from_expr(stmt, call_node):
                        continue

                # Case 2: side effectful method on a reactive object, such as fig.update_layout(...)
                if (
                    isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and isinstance(stmt.value.func.value, ast.Name)
                    and stmt.value.func.value.id in self._current_frame.variable_to_atom
                ):
                    logger.debug('[DEBUG] going to call _lift_side_effect_stmt for %s', stmt.value.func.value.id)
                    self._lift_side_effect_stmt(stmt)
                    continue

                # Case 3: consumer of reactive values, for example: text(f"{x}")
                if self._uses_known_atoms(stmt):
                    self._lift_consumer_stmt(stmt)
                    continue

                # Fallback: preserve as is
                new_body.append(stmt)

            # Handle producer assignments
            elif isinstance(stmt, ast.Assign):
                logger.warning(f"[TRACE] About to lift producer statement: {ast.dump(stmt)}")
                variable_map = stmt_variable_maps.get(stmt, self._current_frame.variable_to_atom)
                if isinstance(stmt.targets[0], ast.Name | ast.Tuple | ast.List | ast.Subscript) and isinstance(stmt.value, ast.expr):
                    self._lift_producer_stmt(stmt, pending_assignments, variable_map)
                    continue
                else:
                    new_body.append(stmt)

            # Handle augmented assignments, such as `x += val`
            elif isinstance(stmt, ast.AugAssign):
                if self._uses_known_atoms(stmt):
                    self._lift_augassign_stmt(stmt)
                else:
                    new_body.append(stmt)

            # Pass through unsupported statement types
            else:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[AST] Preserving unsupported statement as is: {ast.dump(stmt)}")
                new_body.append(stmt)

        new_body.extend(pending_assignments)
        return new_body

    def _get_call_func_name(self, call: ast.Call) -> str:
        """
        Attempts to extract the fully qualified function name from an AST Call node.

        Handles:
          - Simple functions:      `func()`       => "func"
          - Single attribute:      `mod.func()`   => "mod.func"
          - Nested attributes:     `pkg.mod.func()` => "pkg.mod.func"

        Returns:
            A dotted function name string, or "<unknown>" if it cannot be resolved.
        """
        def resolve_attribute(node: ast.AST) -> str | None:
            parts = []
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
                return ".".join(reversed(parts))
            return None

        if isinstance(call.func, ast.Name):
            return call.func.id
        elif isinstance(call.func, ast.Attribute):
            result = resolve_attribute(call.func)
            if result:
                return result

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[AST] Unable to resolve function name for call: {ast.dump(call)}")
        else:
            logger.warning(f"[AST] Unable to resolve function name for call. Enable debug logging for ast dump.")
        return "<unknown>"

    def _has_runtime_execution(self, body: list[ast.stmt]) -> bool:
        """
        Determines whether the script includes a full runtime bootstrap:
        an assignment to a workflow instance followed by a call to `execute`.

        Specifically, it checks for:
          - Assignment: `workflow = get_workflow()` or `workflow = Workflow(...)`
          - Execution:  `workflow.execute()`

        This function ensures we do not inject a second runtime bootstrap
        if the user has already instantiated and executed a workflow manually.

        Args:
            body: List of top-level AST statements in the module.

        Returns:
            True if both workflow assignment and execution are detected, False otherwise.
        """

        assigned_var = None

        for stmt in body:
            # Detect: workflow = get_workflow()
            # OR:     workflow = Workflow(...)
            if isinstance(stmt, ast.Assign):
                if (
                    len(stmt.targets) == 1 and
                    isinstance(stmt.targets[0], ast.Name) and
                    isinstance(stmt.value, ast.Call)
                ):
                    func = stmt.value.func
                    if (
                        isinstance(func, ast.Name) and func.id in {"get_workflow", "Workflow"}
                    ):
                        assigned_var = stmt.targets[0].id

            # Detect: workflow.execute()
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if (
                    isinstance(call.func, ast.Attribute) and
                    isinstance(call.func.value, ast.Name) and
                    call.func.attr == "execute" and
                    call.func.value.id == assigned_var
                ):
                    return True

        return False

    def _build_runtime_imports(self) -> list[ast.stmt]:
        """
        Constructs the import statements required for runtime execution injection.

        Includes:
            - get_workflow()
            - build_component_return_from_value()
            - any display_renderers used (e.g. display_matplotlib_show)
        """
        imports = [
            ast.ImportFrom(
                module="preswald",
                names=[ast.alias(name="get_workflow", asname=None)],
                level=0,
            ),
            ast.ImportFrom(
                module="preswald.interfaces.render.registry",
                names=[
                    ast.alias(name="build_component_return_from_value", asname=None),
                    *[ast.alias(name=fn_name, asname=None) for fn_name in sorted(self._used_display_renderer_fns)],
                ],
                level=0,
            ),
        ]
        return imports

    def _build_runtime_execution(self) -> list[ast.stmt]:
        """
        Builds the AST statements required to run a Preswald script.

        This injects:
            workflow = get_workflow()
            workflow.execute()

        These statements are appended to the module only if the original source
        did not already contain equivalent execution logic, as determined by
        `_has_runtime_execution`.

        Returns:
            A list of AST nodes representing the workflow assignment and execution.
        """
        workflow_assign = ast.Assign(
            targets=[ast.Name(id="workflow", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="get_workflow", ctx=ast.Load()),
                args=[],
                keywords=[],
            ),
        )

        workflow_execute = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="workflow", ctx=ast.Load()),
                    attr="execute",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            )
        )

        return [workflow_assign, workflow_execute]

    def _statically_register_declarative_calls(self, stmts: list[ast.stmt]) -> None:
        """
        Scans the script for calls to known registry functions and applies them statically,
        so they take effect before the transformation proceeds.

        This enables user-defined registration of:
          - register_return_renderer(...)
          - register_output_stream_function(...)
          - register_display_method(...)
          - register_mimetype_component_type(...)
        """

        # TODO: Add support for additional static registry functions
        # like 'register_return_type_hint',
        # 'register_display_renderer', etc.  When called directly from
        # a user script, these must be evaluated statically so that
        # hints are available before AST transformation begins.

        known_registrars = {
            "register_return_renderer": register_return_renderer,
            "register_output_stream_function": register_output_stream_function,
            "register_display_method": register_display_method,
            "register_mimetype_component_type": register_mimetype_component_type,
        }

        for stmt in stmts:
            if not isinstance(stmt, ast.Expr):
                continue

            call = stmt.value
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                continue

            func_name = call.func.id
            if func_name not in known_registrars:
                continue

            try:
                args = [ast.literal_eval(arg) for arg in call.args]
                kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords if kw.arg}

                if func_name == "register_return_renderer":
                    mimetype = kwargs.get("mimetype")
                    component_type = kwargs.get("component_type")

                    # Automatically register component type for mimetype if missing
                    if mimetype and not component_type:
                        resolved = get_component_type_for_mimetype(mimetype)
                        if not resolved:
                            logger.debug(
                                f"[AST] No component registered for mimetype={mimetype!r}, defaulting to 'generic'"
                            )
                            register_mimetype_component_type(mimetype, component_type="generic")

                registrar = known_registrars[func_name]
                registrar(*args, **kwargs)
                logger.debug(f"[AST] Applied static registry call: {func_name}(*{args}, **{kwargs})")

            except Exception as e:
                source_text = ast.unparse(stmt)
                lineno = getattr(stmt, 'lineno', None)
                logger.warning(f"[AST] Failed to statically evaluate {func_name} call at line {lineno}: {e}\n{source_text}")

    def visit_Import(self, node: ast.Import) -> ast.Import: # noqa: N802
        """
        Tracks `import preswald` statements and any aliases used.

        If the import includes an alias, such as `import preswald as p`, the alias is
        recorded in `self.import_aliases` with the value `"preswald"`. This allows
        later analysis to resolve namespaced component calls like `p.text(...)`.

        Args:
            node: An `ast.Import` node representing a top level import statement.

        Returns:
            The original `ast.Import` node, unmodified.
        """
        for alias in node.names:
            if alias.name == "preswald":
                asname = alias.asname or alias.name
                self.import_aliases[asname] = "preswald"
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        """
        Tracks `from preswald.interfaces.components import ...` aliases.

        For each imported component from `preswald.interfaces.components`, this function
        records the name alias used in `self._name_aliases`, allowing later resolution
        of aliased calls.

        Args:
            node: An `ast.ImportFrom` node representing a top-level `from ... import ...` statement.

        Returns:
            The original `ast.ImportFrom` node, unmodified.
        """
        if node.module == "preswald.interfaces.components":
            for alias in node.names:
                actual = alias.name
                asname = alias.asname or actual
                if actual in self.known_components:
                    self._name_aliases[actual] = asname
        return node

    def visit_Module(self, node: ast.Module) -> ast.Module: # noqa: N802, C901
        """
        Entry point for AST transformation. Performs a structured two pass rewrite of the top level module body:

        1. Assigns stable component IDs and atom names to known Preswald components.
        2. Rewrites top level component calls into reactive atoms.
        3. Preserves original statement order ( not in all cases yet though ).
        4. Injects required runtime imports (`get_workflow`) and execution scaffolding (`workflow = get_workflow(); workflow.execute()`).
        5. Tracks variable to atom dependencies for reactivity.
        6. Returns a fully transformed `ast.Module` with atoms and runtime bootstrapping injected.
        """

        self._reset()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[AST] Starting module transformation {variable_to_atom=%s}", self._current_frame.variable_to_atom)
        else:
            logger.info("[AST] Starting module transformation")

        # Preserve original import order
        original_imports = []
        non_import_stmts = []

        self._top_level_user_function_calls = self._collect_top_level_user_calls(node.body)

        for stmt in node.body:
            if isinstance(stmt, ast.Import | ast.ImportFrom):
                original_imports.append(stmt)
            elif isinstance(stmt, ast.FunctionDef):
                self._all_function_defs.append(stmt)
                # Defer visiting the function until we know it's not blackbox lifted
                non_import_stmts.append(stmt)
            else:
                non_import_stmts.append(stmt)

        #
        # First pass
        #

        # Detect return renderer registrations in user script
        self._statically_register_declarative_calls(non_import_stmts)

        # assign stable IDs to component calls and track variable to atom mapping
        component_to_atom_name = self._generate_component_metadata(node.body)

        # Initialize an empty variable map that will be updated per statement
        self._current_frame.stmt_variable_maps, self._current_frame.variable_to_atom = self._generate_stmt_variable_maps(
            node.body, component_metadata=component_to_atom_name
        )

        logger.debug(f"[AST] First pass complete {component_to_atom_name=}")
        logger.debug(f"[AST] Final variable-to-atom map {self._current_frame.variable_to_atom=}")

        # Second pass: lift component calls into reactive atoms

        # Remove workflow bootstrap if already present
        runtime_bootstrap_stmts = []

        if self._has_runtime_execution(non_import_stmts):
            filtered_stmts = []
            for stmt in non_import_stmts:
                if (
                    isinstance(stmt, ast.Assign) and
                    len(stmt.targets) == 1 and
                    isinstance(stmt.targets[0], ast.Name) and
                    stmt.targets[0].id == "workflow" and
                    isinstance(stmt.value, ast.Call)
                ):
                    func = stmt.value.func
                    if (
                        isinstance(func, ast.Name) and func.id in {"get_workflow", "Workflow"}
                    ) or (
                        isinstance(func, ast.Attribute) and func.attr == "Workflow"
                    ):
                        runtime_bootstrap_stmts.append(stmt)
                        continue

                elif (
                    isinstance(stmt, ast.Expr) and
                    isinstance(stmt.value, ast.Call) and
                    isinstance(stmt.value.func, ast.Attribute) and
                    isinstance(stmt.value.func.value, ast.Name) and
                    stmt.value.func.value.id == "workflow" and
                    stmt.value.func.attr == "execute"
                ):
                    runtime_bootstrap_stmts.append(stmt)
                    continue

                filtered_stmts.append(stmt)
        else:
            filtered_stmts = non_import_stmts
            runtime_bootstrap_stmts = []

        # import aliases used for renderable registry lookups
        self.import_aliases = {}
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if alias.asname:
                        self.import_aliases[alias.asname] = alias.name
                    else:
                        self.import_aliases[alias.name] = alias.name
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module and stmt.names:
                    for alias in stmt.names:
                        if alias.asname:
                            self.import_aliases[alias.asname] = f"{stmt.module}.{alias.name}"
                        else:
                            self.import_aliases[alias.name] = f"{stmt.module}.{alias.name}"

        self.generic_visit(node)

        new_body = self._lift_statements(filtered_stmts, component_to_atom_name)

        # Now visit remaining FunctionDefs unless blackboxed
        for stmt in non_import_stmts:
            if isinstance(stmt, ast.FunctionDef):
                if stmt.name not in self._blackbox_lifted_functions:
                    self.visit(stmt)

        original_len = len(node.body)
        new_len = len(self._current_frame.generated_atoms + new_body)

        logger.debug(f"[AST] Generated atom functions {len(self._current_frame.generated_atoms)=}")
        logger.info(f"[AST] Final module rewrite complete {original_len=} -> {new_len=}")

        # logger.debug("[AST] Final transformed module structure:")
        # for idx, stmt in enumerate(self._current_frame.generated_atoms + new_body):
        #     match stmt:
        #         case ast.FunctionDef():
        #             logger.debug(f"  [{idx}] FunctionDef {stmt.name}")
        #         case ast.Assign():
        #             logger.debug(f"  [{idx}] Assign {ast.dump(stmt)}")
        #         case ast.Expr():
        #             logger.debug(f"  [{idx}] Expr {ast.dump(stmt)}")
        #         case _:
        #             logger.debug(f"  [{idx}] Other {ast.dump(stmt)}")

        # TODO: Extend workflow constructor detection to consult
        # `import_aliases`, so that `Wf = Workflow`
        # Check whether get_workflow is already imported
        has_get_workflow_import = any(
            isinstance(stmt, ast.ImportFrom) and
            stmt.module == "preswald" and
            any(alias.name == "get_workflow" for alias in stmt.names)
            for stmt in original_imports
        )

        # Check whether Workflow() is manually constructed
        uses_workflow_constructor = any(
            isinstance(stmt, ast.Assign) and
            isinstance(stmt.value, ast.Call) and (
                (isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "Workflow") or
                (isinstance(stmt.value.func, ast.Attribute) and stmt.value.func.attr == "Workflow")
            )
            for stmt in non_import_stmts
        )

        # Inject the import only if needed
        should_inject_import = not (has_get_workflow_import or uses_workflow_constructor)
        runtime_imports = self._build_runtime_imports() if should_inject_import else []

        if not self._has_runtime_execution(node.body):
            logger.debug('does not have runtime execution')
            runtime_exec = self._build_runtime_execution()
        else:
            logger.debug('has runtime execution')
            runtime_exec = []

        node.body = (
            original_imports +
            runtime_imports +
            self._current_frame.generated_atoms +
            new_body +
            runtime_bootstrap_stmts +
            runtime_exec
        )

        logger.debug("[AST] Inserted import statements for lifted atoms and workflow execution")
        return node

    def _replace_dep_args(
        self,
        call: ast.AST,
        param_mapping: dict[str, str],
        variable_map: dict[str, str] | None = None
    ) -> ast.AST:
        """
        Rewrites variable references in an AST expression to use parameter names based on dependency mapping.

        This is used when lifting code into an atom function. Any variable that depends on another atom is
        replaced with a generic parameter name, such as `param0`, `param1`, etc. so that the function can be
        safely rerun with updated inputs.

        Supports replacements in:
          - Standard variable references: `ast.Name`
          - f-strings: `ast.JoinedStr`, `ast.FormattedValue`

        Args:
            call: The AST node representing the expression or statement to rewrite.
            param_mapping: A dict mapping atom names to function parameter names.
            variable_map: Optional override for variable to atom mapping; defaults to `self.variable_to_atom`.

        Returns:
            A transformed AST node with replaced references.
        """
        variable_map = variable_map or self._current_frame.variable_to_atom

        class DependencyReplacer(ast.NodeTransformer):
            def __init__(
                self,
                variable_to_atom: dict[str, str],
                param_mapping: dict[str, str],
                tuple_returning_atoms: set[str],
                tuple_variable_index: dict[str, int],
            ):
                self.variable_to_atom = variable_to_atom
                self.param_mapping = param_mapping
                self.tuple_returning_atoms = tuple_returning_atoms
                self.tuple_variable_index = tuple_variable_index

            def visit_Name(self, node: ast.Name) -> ast.AST:  # noqa: N802
                if not isinstance(node.ctx, ast.Load):
                    return node

                var_name = node.id
                atom = self.variable_to_atom.get(var_name)
                param = self.param_mapping.get(atom)

                if not atom or not param:
                    return node

                if atom in self.tuple_returning_atoms:
                    try:
                        index = self.tuple_variable_index.get(var_name)
                        if index is not None:
                            return ast.Subscript(
                                value=ast.Name(id=param, ctx=ast.Load()),
                                slice=ast.Constant(value=index),
                                ctx=ast.Load()
                            )
                        else:
                            logger.warning(f"[AST] Could not find tuple index for var {var_name} from atom {atom}")
                            return node
                    except ValueError:
                        logger.warning(f"[AST] Could not determine tuple index for {var_name=} from {atom=}")
                        return node
                else:
                    return ast.Name(id=param, ctx=ast.Load())

            def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.FormattedValue:  # noqa: N802
                node.value = self.visit(node.value)
                return node

            def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.JoinedStr:  # noqa: N802
                node.values = [self.visit(value) for value in node.values]
                return node

        return DependencyReplacer(
            variable_map,
            param_mapping,
            self._current_frame.tuple_returning_atoms,
            self._current_frame.tuple_variable_index,
        ).visit(call)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        # Only support simple single target assignments for now
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            varname = node.targets[0].id

            # Detect constructor call: fig = go.Figure()
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                attr = node.value.func.attr  # such as "Figure"
                base = node.value.func.value  # such as ast.Name(id='go')
                if isinstance(base, ast.Name):
                    base_name = base.id  # such as "go"
                    full_base = self.import_aliases.get(base_name, base_name)  # resolves to full module, such as "plotly.graph_objects"

                    fqcn = f"{full_base}.{attr}"  # such as "plotly.graph_objects.Figure"
                    self._variable_class_map[varname] = fqcn

        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST: # noqa: N802
        """
        Handles function call nodes in the AST and injects reactivity when appropriate.

        Specifically:
          1. Lifts inline Preswald component calls into atoms with stable IDs.
          2. Tracks dependencies between atoms when one atom calls another user defined atom function.
          3. Tracks dependencies for calls to local variables assigned from known component calls.

        This function ensures that all relevant call sites are wired into the reactive DAG.

        Returns:
            The original call node, or a replacement call to a generated atom function.
        """
        # Ensure children are visited before transforming this node
        self.generic_visit(node)

        if not isinstance(node.func, ast.Name):
            return node

        func_name = node.func.id

        # should not be lifting known component calls here
        if self._is_known_component_call(node):
            # We no longer lift component calls from within visit_Call. All such lifting is handled in _lift_statements()
            # This block exists purely as a sanity check to catch unexpected component calls that weren't lifted.

            # Try to guess the name this call would have been lifted into
            guessed_atom_name = self._get_call_func_name(node)
            if guessed_atom_name not in self.dependencies:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        "[AST] visit_Call saw a known component call not lifted by _lift_statements: %s",
                        ast.unparse(node)
                    )
                else:
                    logger.warning(
                        "[AST] visit_Call saw a known component call not lifted by _lift_statements: %s",
                        guessed_atom_name
                    )

        # Case 2: Call to a top level atom lifted function
        for fn in self._all_function_defs:
            if fn.name == func_name and hasattr(fn, "generated_atom_name"):
                callee_atom = fn.generated_atom_name
                caller_atom = getattr(self.current_function, "generated_atom_name", None)
                if caller_atom and callee_atom:
                    self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
                    if logger.isEnabledFor(logging.INFO):
                        logger.debug("[AST] Dependency tracked via function call: %s -> %s", caller_atom, callee_atom)

        # Case 3: Call to variable that references a lifted component
        if func_name in self._current_frame.variable_to_atom:
            callee_atom = self._current_frame.variable_to_atom[func_name]
            caller_atom = getattr(self.current_function, "generated_atom_name", None)
            if caller_atom and callee_atom:
                self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
                if logger.isEnabledFor(logging.INFO):
                    logger.debug("[AST] Dependency tracked via variable call: %s -> %s", caller_atom, callee_atom)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef: # noqa: N802
        self._all_function_defs.append(node)

        if not self._is_top_level(node) and not self._should_inline_function(node.name):
            logger.debug(f"[AST] Skipping transformation of function '{node.name}' (blackbox fallback)")
            return node

        if node.name in self._blackbox_lifted_functions:
            logger.debug(f"[AST] Skipping visit to '{node.name}' because it was already blackbox lifted")
            return node

        # Only lift and traverse if its top level or should inline
        self._in_function_body = True
        prev_function = self.current_function
        self.current_function = node

        if self._is_top_level(node):
            if self._is_undecorated(node) and self._is_user_defined_blackbox_function(node):
                logger.debug(f"[DEBUG] visit_FunctionDef: Skipping top level user function: {node.name}")
                return node

            # Attach atom decorator
            callsite_hint = f"{self.filename}:{getattr(node, 'lineno', 0)}"
            atom_name = generate_stable_id("_auto_atom", callsite_hint=callsite_hint)
            decorator = self._create_workflow_atom_decorator(atom_name, callsite_deps=[])
            node.decorator_list.insert(0, decorator)
            node.generated_atom_name = atom_name
            self.atoms.append(atom_name)

        self._frames.append(Frame())
        try:
            self.generic_visit(node)

            component_metadata = self._generate_component_metadata(node.body)
            self._current_frame.stmt_variable_maps, self._current_frame.variable_to_atom = self._generate_stmt_variable_maps(
                node.body, component_metadata=component_metadata
            )

            node.body = self._lift_statements(node.body, component_metadata=component_metadata)

            for atom in self._current_frame.generated_atoms:
                logger.info(f"[DEBUG] Atom lifted inside function {node.name}: {atom.name}")

        finally:
            self._module_frame.generated_atoms.extend(self._current_frame.generated_atoms)
            self._frames.pop()

        self.current_function = prev_function
        self._in_function_body = False

        atom_name = getattr(node, "generated_atom_name", None)
        deps = self.dependencies.get(atom_name)
        if atom_name and deps:
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "atom"
                ):
                    if not any(kw.arg == "dependencies" for kw in decorator.keywords):
                        decorator.keywords.append(
                            ast.keyword(
                                arg="dependencies",
                                value=ast.List(elts=[ast.Constant(value=dep) for dep in deps], ctx=ast.Load()),
                            )
                        )

        return node

    def _is_top_level(self, node):
        return isinstance(getattr(node, "parent", None), ast.Module)

    def _get_variable_map_for_stmt(self, stmt: ast.stmt) -> dict[str, str]:
        """
        Given a statement, returns the variable-to-atom mapping in scope at its location.
        This respects shadowing by later reassignments.
        """
        return self._current_frame.stmt_variable_maps.get(stmt, self._current_frame.variable_to_atom)

    def _find_dependencies(
        self, node: ast.AST, variable_map: dict[str, str] | None = None
    ) -> tuple[list[str], list[str]]:
        """
        Extracts reactive dependencies from an AST expression.

        Scans for any `ast.Name` or `ast.Attribute` nodes that correspond
        to variables previously bound to atoms via `variable_map`.

        Returns:
            - A list of atom names, in order of appearance, required as inputs
            - A corresponding list of variable names that triggered those dependencies

        This is used to:
          - Determine what parameters an atom function should accept
          - Wire the DAG based on usage of previously reactive values
        """
        variable_map = variable_map or self._current_frame.variable_to_atom
        deps: list[str] = []
        dep_names: list[str] = []

        class Finder(ast.NodeVisitor):
            def visit_Name(self, name_node: ast.Name): # noqa: N802
                if isinstance(name_node.ctx, ast.Load) and name_node.id in variable_map:
                    deps.append(variable_map[name_node.id])
                    dep_names.append(name_node.id)

            def visit_Attribute(self, node: ast.Attribute): # noqa: N802
                # Match expressions like: `val.method()` where `val` is reactive
                if isinstance(node.value, ast.Name) and node.value.id in variable_map:
                    deps.append(variable_map[node.value.id])
                    dep_names.append(node.value.id)
                self.generic_visit(node)

            def generic_visit(self, node):
                super().generic_visit(node)

        finder = Finder()
        #logger.debug(f"[DEBUG] AST node for dependency scan: {ast.dump(node, indent=2)}")
        finder.visit(node)

        return deps, dep_names

    def _make_param_mapping(self, callsite_deps: list[str]) -> dict[str, str]:
         # Map dependency atom names to parameter names like param0, param1, ...
        return {dep: f"param{i}" for i, dep in enumerate(callsite_deps)}

    def _patch_callsite(self, node: ast.Call, callsite_deps: list[str], component_id: str) -> ast.Call:
        """
        Rewrites a component call site by injecting parameterized arguments and a stable component ID.

        This is used to replace original variable references with `param0`, `param1`, ...
        to support rerunnable, dependency aware atoms.

        Args:
            node: The original `ast.Call` node.
            callsite_deps: List of atom names that this call depends on.
            component_id: Stable component ID for reconciliation with the frontend.

        Returns:
            A patched `ast.Call` node with dependency inputs replaced and `component_id` injected.
        """
        # Build dependency-to-parameter mapping
        param_mapping = self._make_param_mapping(callsite_deps)

        # Patch variable references in call args using scoped variable map
        patched_call = self._replace_dep_args(node, param_mapping, variable_map=self._get_variable_map_for_stmt(node))

        # Inject component_id into kwargs if not already present
        existing_kwarg_names = {kw.arg for kw in node.keywords if kw.arg is not None}
        if "component_id" not in existing_kwarg_names:
            patched_call.keywords.append(
                ast.keyword(arg="component_id", value=ast.Constant(value=component_id))
            )

        return patched_call

    def _validate_or_remap_return_target(
        self,
        return_target: ast.expr,
        body: list[ast.stmt],
        param_mapping: dict[str, str]
    ) -> ast.expr:
        """
        Ensures the return_target refers to a variable defined in the function body,
        or remaps it to a known parameter if needed.

        Args:
            return_target: The AST node intended for return (typically ast.Name).
            body: The list of AST statements in the atom function body.
            param_mapping: Maps original dependency variable names to function parameter names.

        Returns:
            A valid ast.expr suitable for use in a return statement.
        """
        if isinstance(return_target, ast.Name):
            var_name = return_target.id
            assigned_names = {
                t.id for stmt in body if isinstance(stmt, ast.Assign)
                for t in stmt.targets if isinstance(t, ast.Name)
            }
            if var_name not in assigned_names:
                if var_name in param_mapping:
                    return ast.Name(id=param_mapping[var_name], ctx=ast.Load())
                else:
                    logger.warning(
                        f"[AST] return_target not found in assignments or param mapping."
                        f"{var_name=} {assigned_names=}"
                    )

        return return_target

    def _build_atom_function(
        self,
        atom_name: str,
        component_id: str,
        callsite_deps: list[str],
        call_expr: ast.AST | list[ast.stmt],
        *,
        return_target: str | list[str] | tuple[str, ...] | ast.expr | None = None
    ) -> ast.FunctionDef:
        """
        Constructs a reactive atom function from a lifted expression or component call.

        The generated function will:
        - Accept `param0`, `param1`, ... as arguments for each reactive dependency
        - Wrap the user expression(s) in a function body
        - Return the computed value (or specified `return_target`)
        - Be decorated with `@workflow.atom(name=..., dependencies=[...])`

        Supports:
        - Named assignments: `x = ...`
        - Subscript assignments: `param0["col"] = ...`
        - Blocks of statements: `list[ast.stmt]`
        - Raw expressions: a value to directly `return`
        - Explicit return override via `return_target`
        """

        # Create function parameters: (param0, param1, ...)
        args_ast = self._make_param_args(callsite_deps)

        # Build decorator
        decorator = self._create_workflow_atom_decorator(atom_name, callsite_deps)

        # Build function body
        if isinstance(call_expr, list):
            body = call_expr
        elif isinstance(call_expr, ast.Assign):
            body = [call_expr]
        elif isinstance(call_expr, ast.Expr):
            body = [call_expr]
        else:
            # e.g. raw expression to return directly
            return_stmt = ast.Return(value=call_expr)
            return ast.FunctionDef(
                name=atom_name,
                args=args_ast,
                body=[return_stmt],
                decorator_list=[decorator],
            )

        # Append appropriate return statement
        if isinstance(return_target, str):
            body.append(ast.Return(value=ast.Name(id=return_target, ctx=ast.Load())))
        elif isinstance(return_target, list | tuple):
            body.append(ast.Return(value=ast.Tuple(
                elts=[ast.Name(id=name, ctx=ast.Load()) for name in return_target],
                ctx=ast.Load()
            )))
        elif isinstance(return_target, ast.expr):
            param_mapping = self._make_param_mapping(callsite_deps)
            return_target = self._validate_or_remap_return_target(return_target, body, param_mapping)
            body.append(ast.Return(value=return_target))
        else:
            body.append(ast.Return(value=ast.Constant(value=None)))

        # Validation for safety
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    assert isinstance(target.ctx, ast.Store), f"Expected Store context, got {type(target.ctx)}"
                    assert isinstance(target, ast.Name | ast.Tuple | ast.List | ast.Subscript), f"Invalid assignment target: {ast.dump(target)}"

        return ast.FunctionDef(
            name=atom_name,
            args=args_ast,
            body=body,
            decorator_list=[decorator],
        )

    def _create_workflow_atom_decorator(self, atom_name: str, callsite_deps: list[str]) -> ast.Call:
        """
        Constructs a decorator expression for @workflow.atom(...).

        Args:
            atom_name: The name to assign to the reactive atom.
            callsite_deps: A list of atom names this atom depends on.

        Returns:
            An `ast.Call` node representing the decorator.
        """

        keywords = [ast.keyword(arg="name", value=ast.Constant(value=atom_name))]
        unique_deps = list(dict.fromkeys(callsite_deps))

        if unique_deps:
            keywords.append(
                ast.keyword(
                    arg="dependencies",
                    value=ast.List(
                        elts=[ast.Constant(value=dep) for dep in unique_deps],
                        ctx=ast.Load(),
                    ),
                )
            )

        return ast.Call(
            func=ast.Attribute(value=ast.Name(id="workflow", ctx=ast.Load()), attr="atom", ctx=ast.Load()),
            args=[],
            keywords=keywords,
        )

    def _make_param_args(self, callsite_deps: list[str]) -> ast.arguments:
        return ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=f"param{i}") for i in range(len(callsite_deps))],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )

    def _make_callsite(self, atom_name: str, dep_names: list[str]) -> ast.Call:
        return ast.Call(
            func=ast.Name(id=atom_name, ctx=ast.Load()),
            args=[ast.Name(id=dep_name, ctx=ast.Load()) for dep_name in dep_names],
            keywords=[]
        )

    def lift_component_call_to_atom(self, node: ast.Call, component_id: str, atom_name: str, variable_map: dict[str, str], *, return_target: str | None = None,) -> ast.Call:
        """
        Wrap a component call into an auto-generated atom function.

        This transformation rewrites the component into a reactive function that:
        - Accepts its dependencies as named parameters.
        - Is decorated with `@workflow.atom(...)` using stable names.
        - Returns the original component call with identifiers replaced by parameters.

        Args:
            node (ast.Call): The original component call.
            component_id (str): A stable ID for this component (used for render tracking).
            atom_name (str): A stable atom name for the generated function.

        Returns:
            ast.Call: A new call to the generated atom function with resolved arguments.
        """

        callsite_deps, dep_names = self._find_unique_dependencies(node, variable_map)
        patched_call = self._patch_callsite(node, callsite_deps, component_id)

        # Generate the atom function that wraps the patched call
        new_func = self._build_atom_function(atom_name, component_id, callsite_deps, patched_call, return_target=return_target)

        self._current_frame.generated_atoms.append(new_func)

        # Register its dependencies for future rewrites
        self.dependencies[atom_name] = set(callsite_deps)

        # Return a call to the new atom, passing in the original variable names
        return self._make_callsite(atom_name, dep_names)

    def _generate_stmt_variable_maps(
        self,
        body: list[ast.stmt],
        component_metadata: dict[int, tuple[str, str]] | None = None,
    ) -> tuple[dict[ast.stmt, dict[str, str]], dict[str, str]]:
        """
        Computes per-statement variable-to-atom maps for a given list of statements.

        Returns:
            - A map of each statement to its scoped variable-to-atom map
            - The final merged variable-to-atom map
        """
        component_metadata = component_metadata or {}
        full_variable_map: dict[str, str] = {}
        stmt_variable_maps: dict[ast.stmt, dict[str, str]] = {}

        for stmt in body:
            variable_map = full_variable_map.copy()

            if isinstance(stmt, ast.Assign):
                call_node = stmt.value if isinstance(stmt.value, ast.Call) else None
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        if (
                            call_node and
                            isinstance(call_node.func, ast.Name) and
                            id(call_node) in component_metadata
                        ):
                            _, atom_name = component_metadata[id(call_node)]
                            variable_map[target.id] = atom_name

            stmt_variable_maps[stmt] = variable_map
            full_variable_map.update(variable_map)

        return stmt_variable_maps, full_variable_map

    def generate_component_and_atom_name(self, func_name: str, stmt: ast.stmt | None = None) -> tuple[str, str]:
        """
        Generates a stable (component_id, atom_name) pair using a callsite hint.

        If a source statement is provided, its real `lineno` is used for the hint.
        Otherwise, an artificial line number is incremented and used instead.
        This ensures deterministic naming even for synthetic or inline expressions.

        Args:
            func_name: Name of the original function or component.
            stmt: Optional AST node to extract source location from.

        Returns:
            A tuple of (component_id, atom_name).
        """

        if stmt and hasattr(stmt, "lineno"):
            callsite_hint = f"{self.filename}:{stmt.lineno}"
        else:
            callsite_hint = f"{self.filename}:{self._artificial_lineno}"
            self._artificial_lineno += 1

        component_id = generate_stable_id(func_name, callsite_hint=callsite_hint)
        atom_name = generate_stable_atom_name_from_component_id(component_id)

        logger.debug(f"[AST] Generated names {func_name=} {callsite_hint=} {component_id=} {atom_name=}")
        return component_id, atom_name


def annotate_parents(tree: ast.AST) -> ast.AST:
    """
    Annotates each AST node in the tree with a `.parent` attribute pointing to its parent node.

    This is used by the transformer to detect top level (module scope) definitions
    and apply scope sensitive transformations, such as lifting only module level functions
    into reactive atoms.

    Args:
        tree: The root AST node

    Returns:
        The same AST tree, with `.parent` attributes added to each node.
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


def transform_source(source: str, filename: str = "<script>") -> tuple[ast.Module, list[str]]:
    """
    Main entry point for transforming a Preswald source script.

    Parses the input Python source code into an AST, annotates it with parent pointers,
    and applies the `AutoAtomTransformer` to lift reactive expressions into atoms.

    Args:
        source: The source code as a string.
        filename: Optional filename used for logging and ID generation.

    Returns:
        A tuple:
            - The transformed AST module
            - A list of generated atom names
    """
    try:
        tree = ast.parse(source, filename=filename)
        annotate_parents(tree)

        transformer = AutoAtomTransformer(filename=filename)
        new_tree = transformer.visit(tree)

        ast.fix_missing_locations(new_tree)

        if logger.isEnabledFor(logging.DEBUG):
            source_code = ast.unparse(new_tree)
            logger.debug("Transformed source code:\n%s", source_code)

        return new_tree, transformer.atoms

    except SyntaxError as syntax_error:
        register_error(
            type="ast_transform",
            filename=filename,
            lineno=syntax_error.lineno or 0,
            message=str(syntax_error),
            source=source,
            component_id=None,
            atom_name=None,
        )
        logger.warning(f"[AST] Syntax error during transform: {syntax_error}")
        return None, []
    except AstHaltError as halt:
        logger.error(f"[AST] Transformation halted: {halt}")
        return None, []
