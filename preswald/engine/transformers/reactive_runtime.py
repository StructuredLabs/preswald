import ast
import logging

from preswald.interfaces import components
from preswald.utils import (
    generate_stable_atom_name_from_component_id,
    generate_stable_id,
)


logger = logging.getLogger(__name__)


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
        self.atoms = []
        self._all_function_defs = []
        self.current_function = None
        self.dependencies = {}
        self.helper_counter = 0
        self.generated_atoms = []
        self.variable_to_atom = {}
        self.known_components = self._discover_known_components()

    def _discover_known_components(self) -> set[str]:
        """
        Discover all component functions in `preswald.interfaces.components`
        that have been marked with a `_preswald_component_type` attribute.

        These are treated as "known" and will be automatically lifted into atoms.

        Returns:
            A set of component function names.
        """
        return {
            name for name in dir(components)
            if getattr(getattr(components, name), "_preswald_component_type", None) is not None
        }

    def _has_callsite_hint(self, call_node):
        return any(kw.arg == "callsite_hint" for kw in call_node.keywords)

    def _should_inject_callsite_hint(self, call_node):
        func_name = getattr(call_node.func, "id", None)
        return func_name in self.known_components

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """
        Entry point for AST transformation. This performs a two-pass rewrite:

        1. Assigns stable component IDs and atom names to known Preswald components.
        2. Rewrites top-level component calls into reactive atoms.

        It also injects import statements required by lifted atoms (e.g., TrackedValue, track_dependency).
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[AST] Starting module transformation {variable_to_atom=%s}", self.variable_to_atom)
        else:
            logger.info("[AST] Starting module transformation")

        original_imports = [stmt for stmt in node.body if isinstance(stmt, (ast.Import, ast.ImportFrom))]

        # First pass: assign stable IDs to component calls and track variable-to-atom mapping
        self.variable_to_atom = {}
        component_to_atom_name = {}

        for stmt in node.body:
            if isinstance(stmt, (ast.Assign, ast.Expr)):
                call_node = stmt.value if isinstance(stmt, ast.Expr) else stmt.value

                if isinstance(call_node, ast.Call) and isinstance(call_node.func, ast.Name):
                    func_name = call_node.func.id

                    if func_name in self.known_components:
                        # Generate a callsite hint using filename and lineno
                        if hasattr(call_node, "lineno"):
                            callsite_hint = f"{self.filename}:{call_node.lineno}"
                        else:
                            callsite_hint = f"{self.filename}:0"

                        component_id = generate_stable_id(func_name, callsite_hint=callsite_hint)
                        atom_name = generate_stable_atom_name_from_component_id(component_id)
                        component_to_atom_name[id(call_node)] = (component_id, atom_name)

                        logger.debug(
                            "[AST] Registered component call {func_name=} {callsite_hint=} "
                            f"{component_id=} {atom_name=}"
                        )

                        # Track variable assignment for use in dependency resolution
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name):
                                    self.variable_to_atom[target.id] = atom_name

        logger.info(f"[AST] First pass complete {component_to_atom_name=}")
        logger.info(f"[AST] Final variable-to-atom map {self.variable_to_atom=}")

        # Reset helper counter before lifting
        self.helper_counter = 0

        # Second pass: lift component calls into reactive atoms
        new_body = []

        for stmt in node.body:
            call_node = None
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value

            if call_node and isinstance(call_node.func, ast.Name):
                func_name = call_node.func.id

                if func_name in self.known_components:
                    component_id, atom_name = component_to_atom_name.get(id(call_node), (None, None))
                    logger.debug(f"[AST] Retrieved atom mapping {func_name=} {component_id=} {atom_name=}")

                    if not atom_name:
                        logger.warning(f"[AST] Missing mapping for call {func_name=} — regenerating")
                        component_id, atom_name = self.generate_component_and_atom_name(func_name)

                    # Lift the call into a new atom definition
                    self.lift_component_call_to_atom(call_node, component_id, atom_name)
                    continue

            # Preserve non-components
            if not isinstance(stmt, (ast.Import, ast.ImportFrom)):
                new_body.append(stmt)

        original_len = len(node.body)
        new_len = len(self.generated_atoms + new_body)

        logger.info(f"[AST] Generated atom functions {len(self.generated_atoms)=}")
        logger.info(f"[AST] Final module rewrite complete {original_len=} -> {new_len=}")

        logger.debug("[AST] Final transformed module structure:")
        for idx, stmt in enumerate(self.generated_atoms + new_body):
            match stmt:
                case ast.FunctionDef():
                    logger.debug(f"  [{idx}] FunctionDef {stmt.name}")
                case ast.Assign():
                    logger.debug(f"  [{idx}] Assign {ast.dump(stmt)}")
                case ast.Expr():
                    logger.debug(f"  [{idx}] Expr {ast.dump(stmt)}")
                case _:
                    logger.debug(f"  [{idx}] Other {ast.dump(stmt)}")
        import_nodes = []
        # Inject get_workflow import for atom execution
        import_get_workflow = ast.ImportFrom(
            module="preswald",
            names=[ast.alias(name="get_workflow", asname=None)],
            level=0,
        )
        #node.body.insert(2, import_get_workflow)
        import_nodes.append(import_get_workflow)

        # Create: workflow = get_workflow()
        workflow_assign = ast.Assign(
            targets=[ast.Name(id="workflow", ctx=ast.Store())],
            value=ast.Call(func=ast.Name(id="get_workflow", ctx=ast.Load()), args=[], keywords=[]),
        )

        # Create: workflow.execute()
        workflow_execute = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(value=ast.Name(id="workflow", ctx=ast.Load()), attr="execute", ctx=ast.Load()),
                args=[],
                keywords=[],
            )
        )

        node.body = original_imports + import_nodes + self.generated_atoms + [workflow_assign] + new_body + [workflow_execute]
        logger.info("[AST] Inserted import statements for lifted atoms and workflow execution")
        return node

    def _replace_dep_args(self, call, param_mapping):
        class DependencyReplacer(ast.NodeTransformer):
            def __init__(self, variable_to_atom, param_mapping):
                self.variable_to_atom = variable_to_atom
                self.param_mapping = param_mapping

            def visit_Name(self, node):
                if node.id in self.variable_to_atom:
                    atom = self.variable_to_atom[node.id]
                    mapped = self.param_mapping.get(atom)
                    if mapped:
                        return ast.Name(id=mapped, ctx=ast.Load())
                return node

            def visit_FormattedValue(self, node):
                node.value = self.visit(node.value)
                return node

            def visit_JoinedStr(self, node):
                node.values = [self.visit(value) for value in node.values]
                return node

        replacer = DependencyReplacer(self.variable_to_atom, param_mapping)
        return replacer.visit(call)

    def visit_Call(self, node):
        """
        Rewrites function calls into reactive atoms or registers dependencies.

        This method is called for every function call in the AST. It performs three roles:

        1. If the call is to a known Preswald component (e.g., `slider`, `text`), it is lifted
           into a reactive atom with a stable ID and replaced with a call to the generated atom.

        2. If the call is to another top-level function that was lifted into an atom earlier,
           it records the callee atom as a dependency of the current atom.

        3. If the call is to a local variable assigned from a component call (e.g., `val = slider()`),
           it infers the atom from that assignment and tracks the dependency accordingly.

        This dependency information is used later to build the DAG of reactive relationships.

        Returns:
            ast.AST: The original or transformed call node.
        """
        # Visit all children first to ensure proper traversal
        self.generic_visit(node)

        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            # Case 1: This is a known Preswald component (e.g., slider, text, etc.)
            if func_name in self.known_components:
                component_id, atom_name = self.generate_component_and_atom_name(func_name)
                logger.info(f"[AST] Lifting inline component call {func_name=} {component_id=} {atom_name=}")
                return self.lift_component_call_to_atom(node, component_id, atom_name)

            # Case 2: This call targets a previously defined top-level function
            for fn in self._all_function_defs:
                if fn.name == func_name and hasattr(fn, "generated_atom_name"):
                    callee_atom = fn.generated_atom_name
                    caller_atom = getattr(self.current_function, "generated_atom_name", None)
                    if caller_atom and callee_atom:
                        self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
                        logger.debug(f"[AST] Tracking dependency via FunctionDef {caller_atom=} -> {callee_atom=}")

            # Case 3: This call references a lifted component assigned to a variable
            if func_name in self.variable_to_atom:
                callee_atom = self.variable_to_atom[func_name]
                caller_atom = getattr(self.current_function, "generated_atom_name", None)
                if caller_atom and callee_atom:
                    self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
                    logger.debug(f"[AST] Tracking dependency via variable {caller_atom=} -> {callee_atom=}")

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Visits top-level function definitions and lifts them into reactive atoms.

        This method performs the following:
        1. Detects if the function is at module scope (i.e. top-level).
        2. Decorates it with `@workflow.atom(name=...)` using a stable atom name.
        3. Tracks the function for dependency mapping.
        4. After visiting its body, if any dependencies were registered for the atom,
           it injects them into the atom decorator's `dependencies` argument.

        Returns:
            ast.FunctionDef: The potentially modified function node.
        """
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
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value=atom_name))
                ],
            )
            node.decorator_list.insert(0, decorator)
            node.generated_atom_name = atom_name
            self.atoms.append(atom_name)

        self._all_function_defs.append(node)
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None

        if hasattr(node, "generated_atom_name"):
            atom_name = node.generated_atom_name
            deps = self.dependencies.get(atom_name)
            if deps:
                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Attribute)
                        and decorator.func.attr == "atom"
                    ):
                        existing_keys = {kw.arg for kw in decorator.keywords}
                        if "dependencies" not in existing_keys:
                            # Preserve insertion order of dependencies
                            callsite_deps = list(deps)
                            decorator.keywords.append(
                                ast.keyword(
                                    arg="dependencies",
                                    value=ast.List(
                                        elts=[ast.Constant(value=dep) for dep in callsite_deps],
                                        ctx=ast.Load()
                                    )
                                )
                            )

        return node

    def _is_top_level(self, node):
        return isinstance(getattr(node, "parent", None), ast.Module)

    def lift_component_call_to_atom(self, node: ast.Call, component_id: str, atom_name: str) -> ast.Call:
        """
        Wrap a component call (e.g., slider(), text()) into an auto-generated atom function.

        This transformation rewrites the component into a reactive function that:
        - Accepts its dependencies as named parameters.
        - Is decorated with `@workflow.atom(...)` using stable names.
        - Returns the original component call with identifiers replaced by parameters.

        Args:
            node (ast.Call): The original component call (e.g., `slider(...)`).
            component_id (str): A stable ID for this component (used for render tracking).
            atom_name (str): A stable atom name for the generated function.

        Returns:
            ast.Call: A new call to the generated atom function with resolved arguments.
        """
        callsite_deps = []  # atom names the component depends on
        dep_names = []      # user variable names used in the callsite

        # Identify callsite arguments that map to other atoms (dependencies)
        for arg in node.args:
            if isinstance(arg, ast.Name) and arg.id in self.variable_to_atom:
                callsite_deps.append(self.variable_to_atom[arg.id])
                dep_names.append(arg.id)
            elif isinstance(arg, ast.JoinedStr):
                for value in arg.values:
                    if isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name):
                        if value.value.id in self.variable_to_atom:
                            callsite_deps.append(self.variable_to_atom[value.value.id])
                            dep_names.append(value.value.id)

        for kw in node.keywords:
            if isinstance(kw.value, ast.Name) and kw.value.id in self.variable_to_atom:
                callsite_deps.append(self.variable_to_atom[kw.value.id])
                dep_names.append(kw.value.id)

        # Map dependency atom names to parameter names like param0, param1, ...
        param_mapping = {dep: f"param{i}" for i, dep in enumerate(callsite_deps)}

        # Replace variable references with generic param names
        patched_call = self._replace_dep_args(node, param_mapping)

        # Inject component_id if not already present
        existing_kwarg_names = {kw.arg for kw in node.keywords if kw.arg is not None}
        if "component_id" not in existing_kwarg_names:
            patched_call.keywords.append(
                ast.keyword(arg="component_id", value=ast.Constant(value=component_id))
            )

        # Create the parameter list for the generated atom
        args_ast = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=f"param{i}") for i in range(len(callsite_deps))],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )

        # Build the @workflow.atom(...) decorator
        keywords = [ast.keyword(arg="name", value=ast.Constant(value=atom_name))]
        if callsite_deps:
            keywords.append(
                ast.keyword(
                    arg="dependencies",
                    value=ast.List(
                        elts=[ast.Constant(value=dep) for dep in callsite_deps],
                        ctx=ast.Load(),
                    ),
                )
            )

        decorator = ast.Call(
            func=ast.Attribute(value=ast.Name(id="workflow", ctx=ast.Load()), attr="atom", ctx=ast.Load()),
            args=[],
            keywords=keywords,
        )

        # Generate the atom function that wraps the patched call
        new_func = ast.FunctionDef(
            name=atom_name,
            args=args_ast,
            body=[ast.Return(value=patched_call)],
            decorator_list=[decorator],
        )

        self.generated_atoms.append(new_func)

        # Register its dependencies for future rewrites
        self.dependencies[atom_name] = callsite_deps

        # Return a call to the new atom, passing in the original variable names
        return ast.Call(
            func=ast.Name(id=atom_name, ctx=ast.Load()),
            args=[ast.Name(id=dep_name, ctx=ast.Load()) for dep_name in dep_names],
            keywords=[]
        )

    def generate_component_and_atom_name(self, func_name: str) -> tuple[str, str]:
        """
        Generate a component ID and atom name based on the function name and filename context.
        """
        callsite_hint = f"{self.filename}:{self.helper_counter}"
        component_id = generate_stable_id(func_name, callsite_hint=callsite_hint)
        atom_name = generate_stable_atom_name_from_component_id(component_id)
        self.helper_counter += 1
        return component_id, atom_name


def annotate_parents(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    return tree


def transform_source(source: str, filename="<script>"):
    tree = ast.parse(source, filename=filename)
    annotate_parents(tree)
    transformer = AutoAtomTransformer(filename=filename)
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    if logger.isEnabledFor(logging.DEBUG):
        source_code = ast.unparse(new_tree)
        logger.info("Transformed source code:\n%s", source_code)

    return new_tree, transformer.atoms
