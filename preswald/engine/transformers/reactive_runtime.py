import ast
import copy
import logging
from collections import defaultdict

from preswald.interfaces import components
from preswald.utils import (
    generate_stable_atom_name_from_component_id,
    generate_stable_id,
)


logger = logging.getLogger(__name__)

ARTIFICIAL_LINE_NUMBER_START = 100_000 # Used when node call has no lineno attribute. Assumes that nobody has a user script with code on line >= 100,000


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

        self.atoms = []
        self.generated_atoms = []
        self.variable_to_atom = {}
        self._used_linenos = set()
        self._artificial_lineno = ARTIFICIAL_LINE_NUMBER_START
        self.tuple_returning_atoms: set[str] = set()


    def _reset(self):
        self.current_function = None
        self.dependencies = {}
        self._all_function_defs = []
        self.atoms = []
        self.generated_atoms = []
        self.variable_to_atom = {}
        self._used_linenos = set()
        self._artificial_lineno = ARTIFICIAL_LINE_NUMBER_START

    def _discover_known_components(self) -> set[str]:
        """
        Returns a set of component function names defined in `preswald.interfaces.components`
        that are marked with the `_preswald_component_type` attribute.

        These are considered "known components" and are eligible for automatic atom lifting.
        """
        known_components = set()
        for name in dir(components):
            obj = getattr(components, name, None)
            if getattr(obj, "_preswald_component_type", None) is not None:
                known_components.add(name)
        return known_components

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
            call_node = stmt.value if isinstance(stmt, ast.Expr) else getattr(stmt, "value", None)

            if isinstance(call_node, ast.Call) and isinstance(call_node.func, ast.Name):
                func_name = call_node.func.id

                if func_name in self.known_components:
                    lineno = self._get_stable_lineno(call_node, f"Call to {func_name}")
                    callsite_hint = f"{self.filename}:{lineno}"
                    component_id = generate_stable_id(func_name, callsite_hint=callsite_hint)
                    atom_name = generate_stable_atom_name_from_component_id(component_id)

                    component_to_atom_name[id(call_node)] = (component_id, atom_name)

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[AST] Discovered component call {func_name=} {component_id=} {atom_name=}")

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
                self.variable_to_atom[target.id] = atom_name
                logger.debug(f"[AST] bound variable to atom {target.id=} {atom_name=}")

    def _uses_known_atoms(self, stmt: ast.stmt, variable_map: dict[str, str] | None = None) -> bool:
        """
        Detects if a statement uses any reactive (atom-bound) variables.

        This method checks whether the given AST statement references any variable
        that maps to an existing atom. This is used to determine whether a statement
        should be lifted into a reactive atom (e.g., consumer expressions or augmented
        assignments with reactive inputs).

        Args:
            stmt (ast.stmt): The statement to inspect.
            variable_map (dict[str, str] | None): Optional override of variable-to-atom map;
                if not provided, defaults to `self.variable_to_atom`.

        Returns:
            bool: True if the statement depends on one or more atoms.
        """
        variable_map = variable_map or self.variable_to_atom

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
        self, expr: ast.expr, variable_map: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        """
        Resolve reactive dependencies for a given expression node.

        This function determines which variables in the expression map to atoms,
        and returns a de-duplicated list of atom dependencies (`unique_callsite_deps`)
        along with the original variable names (`dep_names`) they came from.

        Args:
            expr: An AST expression node to analyze.
            variable_map: A mapping of variable names to atom names.

        Returns:
            A tuple:
                - unique_callsite_deps: list of atom names (deduplicated, order-preserved)
                - dep_names: list of variable names used in the expression
        """
        callsite_deps, dep_names = self._find_dependencies(expr, variable_map)
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

        scoped_map = {**self.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        target = stmt.target

        if not isinstance(target, ast.Name):
            raise ValueError("Only simple names are supported in AugAssign for now")

        callsite_deps, dep_names = self._find_unique_dependencies(stmt, scoped_map)

        # Ensure the LHS variable is included as a dependency
        lhs_atom = scoped_map.get(target.id)
        if lhs_atom and lhs_atom not in callsite_deps:
            callsite_deps.insert(0, lhs_atom)
            dep_names.insert(0, target.id)

        component_id, atom_name = self.generate_component_and_atom_name("producer")
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
        self.variable_to_atom[target.id] = atom_name
        func = self._build_atom_function(atom_name, component_id, callsite_deps, call_expr=assign_stmt)
        self.generated_atoms.append(func)

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
        scoped_map = {**self.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}

        if isinstance(stmt.targets[0], ast.Tuple | ast.List):
            component_id, atom_name = self.generate_component_and_atom_name("producer")
            self.tuple_returning_atoms.add(atom_name)

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

            return_stmt = ast.Return(value=ast.Tuple(
                elts=[
                    ast.Name(id=elt.id, ctx=ast.Load())
                    for elt in stmt.targets[0].elts
                    if isinstance(elt, ast.Name)
                ],
                ctx=ast.Load()
            ))

            body = [temp_assign, unpack_assign, return_stmt]
            callsite_deps, dep_names = self._find_unique_dependencies(ast.Module(body=body, type_ignores=[]), scoped_map)
            param_mapping = self._make_param_mapping(callsite_deps)
            patched_expr = [self._replace_dep_args(stmt, param_mapping, variable_map) for stmt in body]

            logger.debug(f"[AST] Lifted tuple unpacking producer: {atom_name=} {callsite_deps=}")

            for elt in stmt.targets[0].elts:
                if isinstance(elt, ast.Name):
                    variable_map[elt.id] = atom_name

        else:
            component_id, atom_name = self.generate_component_and_atom_name("producer")
            callsite_deps, dep_names = self._find_unique_dependencies(stmt.value, scoped_map)
            param_mapping = self._make_param_mapping(callsite_deps)
            patched_expr = ast.Assign(
                targets=stmt.targets,
                value=self._replace_dep_args(stmt.value, param_mapping, scoped_map)
            )

            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    variable_map[target.id] = atom_name

        self._register_variable_bindings(stmt, atom_name)
        func = self._build_atom_function(
            atom_name,
            component_id,
            callsite_deps,
            call_expr=patched_expr
        )
        self.generated_atoms.append(func)
        self.dependencies[atom_name] = set(callsite_deps)
        self.variable_to_atom.update(variable_map)

    def _lift_consumer_stmt(self, stmt: ast.Expr) -> ast.Expr:
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


        scoped_map = {**self.variable_to_atom, **self._get_variable_map_for_stmt(stmt)}
        expr = stmt.value
        callsite_deps, dep_names = self._find_unique_dependencies(expr, variable_map=scoped_map)
        component_id, atom_name = self.generate_component_and_atom_name("consumer")

        # Group variables by originating atom
        atom_to_vars: dict[str, list[str]] = defaultdict(list)
        for var in dep_names:
            atom_to_vars[scoped_map[var]].append(var)

        # Build reverse lookup from variable -> parameter expression
        reverse_map: dict[str, ast.expr] = {}
        for i, atom in enumerate(callsite_deps):
            param_name = f"param{i}"
            for j, var in enumerate(atom_to_vars[atom]):
                if atom not in self.tuple_returning_atoms:
                    reverse_map[var] = ast.Name(id=param_name, ctx=ast.Load())
                else:
                    reverse_map[var] = ast.Subscript(
                        value=ast.Name(id=param_name, ctx=ast.Load()),
                        slice=ast.Constant(value=j),
                        ctx=ast.Load()
                    )

        patched_expr = TupleAwareReplacer().visit(copy.deepcopy(expr))
        ast.fix_missing_locations(patched_expr)

        new_func = self._build_atom_function(atom_name, component_id, callsite_deps, patched_expr)
        self.generated_atoms.append(new_func)

        # Return the rewritten expression as a call to the generated atom
        callsite = self._make_callsite(atom_name, callsite_deps)
        return ast.Expr(value=callsite)

    def _lift_top_level_statements( # noqa: C901
        self,
        body: list[ast.stmt],
        component_metadata: dict[int, tuple[str, str]],
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
        new_body = []
        pending_assignments = []

        for stmt in body:
            # Skip imports as they are handled separately
            if isinstance(stmt, ast.Import | ast.ImportFrom):
                continue

            call_node = None
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value

            # Handle known component calls via metadata
            if call_node and isinstance(call_node.func, ast.Name):
                func_name = call_node.func.id

                if func_name in self.known_components:
                    component_id, atom_name = component_metadata.get(id(call_node), (None, None))

                    if not atom_name:
                        # Fallback path in case metadata was not precomputed
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"[AST] Missing atom mapping for {func_name=}. Regenerating...")
                        component_id, atom_name = self.generate_component_and_atom_name(func_name)

                    if self._uses_known_atoms(stmt):
                        self._lift_consumer_stmt(stmt)
                    else:
                        self.lift_component_call_to_atom(call_node, component_id, atom_name)

                    continue  # statement handled, skip to next

            # Handle expression consumers
            if isinstance(stmt, ast.Expr):
                if self._uses_known_atoms(stmt):
                    self._lift_consumer_stmt(stmt)
                else:
                    new_body.append(stmt)

            # Handle producer assignments
            elif isinstance(stmt, ast.Assign):
                variable_map = self._get_variable_map_for_stmt(stmt)
                if self._uses_known_atoms(stmt, variable_map):
                    self._lift_producer_stmt(stmt, pending_assignments, variable_map)
                else:
                    # Fallback: check if any future statement uses this variable reactively
                    for future_stmt in body:
                        if self._uses_known_atoms(future_stmt, {**variable_map, **self.variable_to_atom}):
                            self._lift_producer_stmt(stmt, pending_assignments, variable_map)
                            break
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
                new_body.append(stmt)

        new_body.extend(pending_assignments)
        return new_body

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
        Constructs the import statement required for runtime execution injection.

        Specifically, this returns:
            from preswald import get_workflow

        This import is required if the script does not already contain a call to
        `workflow = get_workflow()` and `workflow.execute()`. see `_has_runtime_execution`.

        Returns:
            A list containing a single `ast.ImportFrom` node.
        """
        return [
            ast.ImportFrom(
                module="preswald",
                names=[ast.alias(name="get_workflow", asname=None)],
                level=0,
            )
        ]

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
            logger.debug("[AST] Starting module transformation {variable_to_atom=%s}", self.variable_to_atom)
        else:
            logger.info("[AST] Starting module transformation")

        # Preserve original import order
        original_imports = []
        non_import_stmts = []

        for stmt in node.body:
            if isinstance(stmt, ast.Import | ast.ImportFrom):
                original_imports.append(stmt)
            else:
                non_import_stmts.append(stmt)

        # First pass: assign stable IDs to component calls and track variable to atom mapping
        component_to_atom_name = self._generate_component_metadata(node.body)

        # Initialize an empty variable map that will be updated per statement
        full_variable_map = {}
        variable_maps = []

        for stmt in node.body:
            variable_map = full_variable_map.copy()
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        call_node = stmt.value if isinstance(stmt.value, ast.Call) else None
                        if call_node and id(call_node) in component_to_atom_name:
                            _, atom_name = component_to_atom_name[id(call_node)]
                            variable_map[target.id] = atom_name
            variable_maps.append(variable_map)
            full_variable_map.update(variable_map)

        self.variable_to_atom = full_variable_map
        self._stmt_variable_maps = dict(zip(node.body, variable_maps, strict=False))  # store per statement scope

        logger.info(f"[AST] First pass complete {component_to_atom_name=}")
        logger.info(f"[AST] Final variable-to-atom map {self.variable_to_atom=}")

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

        new_body = self._lift_top_level_statements(filtered_stmts, component_to_atom_name)

        original_len = len(node.body)
        new_len = len(self.generated_atoms + new_body)

        logger.info(f"[AST] Generated atom functions {len(self.generated_atoms)=}")
        logger.info(f"[AST] Final module rewrite complete {original_len=} -> {new_len=}")

        logger.info("[AST] Final transformed module structure:")
        for idx, stmt in enumerate(self.generated_atoms + new_body):
            match stmt:
                case ast.FunctionDef():
                    logger.info(f"  [{idx}] FunctionDef {stmt.name}")
                case ast.Assign():
                    logger.info(f"  [{idx}] Assign {ast.dump(stmt)}")
                case ast.Expr():
                    logger.info(f"  [{idx}] Expr {ast.dump(stmt)}")
                case _:
                    logger.info(f"  [{idx}] Other {ast.dump(stmt)}")

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
            logger.info('does not have runtime execution')
            runtime_exec = self._build_runtime_execution()
        else:
            logger.info('has runtime execution')
            runtime_exec = []

        node.body = (
            original_imports +
            runtime_imports +
            self.generated_atoms +
            new_body +
            runtime_bootstrap_stmts +
            runtime_exec
        )

        logger.info("[AST] Inserted import statements for lifted atoms and workflow execution")
        return node

    def _replace_dep_args(self, call: ast.AST, param_mapping: dict[str, str], variable_map: dict[str, str] | None = None) -> ast.AST:
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
        variable_map = variable_map or self.variable_to_atom

        class DependencyReplacer(ast.NodeTransformer):
            def __init__(self, variable_to_atom: dict[str, str], param_mapping: dict[str, str]):
                self.variable_to_atom = variable_to_atom
                self.param_mapping = param_mapping

            def visit_Name(self, node: ast.Name) -> ast.AST: # noqa: N802
                if not isinstance(node.ctx, ast.Load):
                    return node  # Skip Store/Del contexts

                atom = self.variable_to_atom.get(node.id)
                mapped = self.param_mapping.get(atom)

                if mapped:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("[AST] Replacing dependency %s -> %s (from atom=%s)", node.id, mapped, atom)
                    return ast.Name(id=mapped, ctx=ast.Load())

                return node

            def visit_FormattedValue(self, node: ast.FormattedValue) -> ast.FormattedValue: # noqa: N802
                node.value = self.visit(node.value)
                return node

            def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.JoinedStr: # noqa: N802
                node.values = [self.visit(value) for value in node.values]
                return node

        return DependencyReplacer(variable_map, param_mapping).visit(call)

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

        # Case 1: Inline Preswald component call
        if func_name in self.known_components:
            component_id, atom_name = self.generate_component_and_atom_name(func_name)
            if logger.isEnabledFor(logging.INFO):
                logger.info("[AST] Lifting inline component call %s -> %s", func_name, atom_name)
            return self.lift_component_call_to_atom(node, component_id, atom_name)

        # Case 2: Call to a top level atom lifted function
        for fn in self._all_function_defs:
            if fn.name == func_name and hasattr(fn, "generated_atom_name"):
                callee_atom = fn.generated_atom_name
                caller_atom = getattr(self.current_function, "generated_atom_name", None)
                if caller_atom and callee_atom:
                    self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("[AST] Dependency tracked via function call: %s -> %s", caller_atom, callee_atom)

        # Case 3: Call to variable that references a lifted component
        if func_name in self.variable_to_atom:
            callee_atom = self.variable_to_atom[func_name]
            caller_atom = getattr(self.current_function, "generated_atom_name", None)
            if caller_atom and callee_atom:
                self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("[AST] Dependency tracked via variable call: %s -> %s", caller_atom, callee_atom)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef: # noqa: N802
        """
        Visits top level function definitions and lifts them into reactive atoms.

        This transformation enables functions defined at module scope to participate in the
        reactive DAG and automatically rerun when their dependencies change.

        If used in a reactive chain, the function will be:
          - Decorated with `@workflow.atom(...)` and given a stable atom name
          - Tracked in `self.atoms` and `self.dependencies` for DAG construction
          - Injected with explicit `dependencies=[...]` if applicable

        Returns:
            The potentially modified `FunctionDef` node.
        """
        # Detect top-level function and register it as an atom
        if self._is_top_level(node):
            callsite_hint = f"{self.filename}:{getattr(node, 'lineno', 0)}"
            atom_name = generate_stable_id("_auto_atom", callsite_hint=callsite_hint)

            decorator = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="workflow", ctx=ast.Load()),
                    attr="atom",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[ast.keyword(arg="name", value=ast.Constant(value=atom_name))]
            )

            node.decorator_list.insert(0, decorator)
            node.generated_atom_name = atom_name
            self.atoms.append(atom_name)

        # Register for dependency tracking
        self._all_function_defs.append(node)
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None

        # Inject `dependencies=[...]` if any were recorded
        atom_name = getattr(node, "generated_atom_name", None)
        deps = self.dependencies.get(atom_name)

        if atom_name and deps:
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr == "atom"
                ):
                    existing_keys = {kw.arg for kw in decorator.keywords}
                    if "dependencies" not in existing_keys:
                        decorator.keywords.append(
                            ast.keyword(
                                arg="dependencies",
                                value=ast.List(
                                    elts=[ast.Constant(value=dep) for dep in deps],
                                    ctx=ast.Load()
                                )
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
        return self._stmt_variable_maps.get(stmt, self.variable_to_atom)

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
        variable_map = variable_map or self.variable_to_atom
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

        finder = Finder()
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

    def _build_atom_function(
        self,
        atom_name: str,
        component_id: str,
        callsite_deps: list[str],
        call_expr: ast.AST | list[ast.stmt],
    ) -> ast.FunctionDef:
        """
        Constructs a reactive atom function from a lifted expression or component call.

        The generated function will:
          - Accept `param0`, `param1`, ... for each reactive dependency
          - Wrap the user expression(s) in a function body
          - Return the computed value
          - Be decorated with @workflow.atom(name=..., dependencies=[...])

        This is the primary code generation step for converting lifted user code into
        declarative DAG-backed atoms.

        Args:
            atom_name: Stable atom name for the function.
            component_id: Unique component ID (used for reconciliation on frontend).
            callsite_deps: List of atom names this atom depends on.
            call_expr: AST node or list of nodes to wrap in the function body.

        Returns:
            An `ast.FunctionDef` node representing the atom.
        """
        # Create function parameters: (param0, param1, ...)
        args_ast = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=f"param{i}") for i in range(len(callsite_deps))],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )

        # Create the @workflow.atom(name=..., dependencies=...) decorator
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

        decorator = ast.Call(
            func=ast.Attribute(value=ast.Name(id="workflow", ctx=ast.Load()), attr="atom", ctx=ast.Load()),
            args=[],
            keywords=keywords,
        )

        # Determine function body based on type of expression
        if isinstance(call_expr, list):
            body = call_expr
        elif isinstance(call_expr, ast.Assign):
            # e.g. x = ...
            body = [call_expr]
            if isinstance(call_expr.targets[0], ast.Name):
                result = ast.Name(id=call_expr.targets[0].id, ctx=ast.Load())
                body.append(ast.Return(value=result))
            else:
                raise ValueError("Assignment must target a named variable")
        else:
            # e.g. return expr
            body = [ast.Return(value=call_expr)]

        # Validate assignments in generated body
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    assert isinstance(target.ctx, ast.Store), f"Expected Store context, got {type(target.ctx)}"
                    assert isinstance(target, ast.Name |ast.Tuple | ast.List), f"Invalid assignment target: {ast.dump(target)}"

        return ast.FunctionDef(
            name=atom_name,
            args=args_ast,
            body=body,
            decorator_list=[decorator],
        )

    def _make_callsite(self, atom_name: str, dep_names: list[str]) -> ast.Call:
        return ast.Call(
            func=ast.Name(id=atom_name, ctx=ast.Load()),
            args=[ast.Name(id=dep_name, ctx=ast.Load()) for dep_name in dep_names],
            keywords=[]
        )

    def lift_component_call_to_atom(self, node: ast.Call, component_id: str, atom_name: str) -> ast.Call:
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

        callsite_deps, dep_names = self._find_dependencies(node)
        patched_call = self._patch_callsite(node, callsite_deps, component_id)

        # Generate the atom function that wraps the patched call
        new_func = self._build_atom_function(atom_name, component_id, callsite_deps, patched_call)

        self.generated_atoms.append(new_func)

        # Register its dependencies for future rewrites
        self.dependencies[atom_name] = callsite_deps

        # Return a call to the new atom, passing in the original variable names
        return self._make_callsite(atom_name, dep_names)

    def generate_component_and_atom_name(self, func_name: str) -> tuple[str, str]:
        """
        Generates a stable `component_id` and corresponding `atom_name` for a lifted component call.

        Unlike other code paths that may use real source line numbers when available,
        this method always uses a synthetic callsite hint derived from the filename and
        an artificial line number counter. This ensures unique and deterministic naming
        for inline calls discovered during traversal (e.g., inside `visit_Call` or fallback logic).

        Args:
            func_name: The name of the original component function

        Returns:
            A tuple of (component_id, atom_name), both guaranteed to be stable.
        """

        callsite_hint = f"{self.filename}:{self._artificial_lineno}"
        component_id = generate_stable_id(func_name, callsite_hint=callsite_hint)
        atom_name = generate_stable_atom_name_from_component_id(component_id)

        logger.debug(f"[AST] Generated stable names {func_name=} {callsite_hint=} {component_id=} {atom_name=}")
        self._artificial_lineno += 1
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
    tree = ast.parse(source, filename=filename)
    annotate_parents(tree)

    transformer = AutoAtomTransformer(filename=filename)
    new_tree = transformer.visit(tree)

    ast.fix_missing_locations(new_tree)

    if logger.isEnabledFor(logging.DEBUG):
        source_code = ast.unparse(new_tree)
        logger.debug("Transformed source code:\n%s", source_code)

    return new_tree, transformer.atoms
