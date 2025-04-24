import ast

import logging
from preswald.utils import generate_stable_id, generate_stable_atom_id_from_component_id
from preswald.interfaces import components

logger = logging.getLogger(__name__)


class AutoAtomTransformer(ast.NodeTransformer):
    def __init__(self, filename="<script>"):
        self.filename = filename
        self.atoms = []
        self._all_function_defs = []
        self.current_function = None
        self.dependencies = {}
        self.generated_helpers = []
        self.helper_counter = 0
        self.variable_to_atom = {}

        self.known_components = self._discover_known_components()

    def _discover_known_components(self):
        return {
            name for name in dir(components)
            if getattr(getattr(components, name), "_preswald_component_type", None)
        }

    def _has_callsite_hint(self, call_node):
        return any(kw.arg == "callsite_hint" for kw in call_node.keywords)

    def _should_inject_callsite_hint(self, call_node):
        func_name = getattr(call_node.func, "id", None)
        return func_name in self.known_components

    def visit_Module(self, node):
        logger.info(f'variable_to_atom={self.variable_to_atom}')

        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                call_node = stmt.value
                component_type = getattr(call_node.func, 'id', 'component')
                callsite_hint = f"{self.filename}:{getattr(call_node, 'lineno', 0)}"
                component_id = generate_stable_id(component_type, callsite_hint=callsite_hint)
                stable_name = generate_stable_atom_id_from_component_id(component_id)
                logger.info(f"first pass - stable_name: {stable_name}")
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        self.variable_to_atom[target.id] = stable_name
                self.helper_counter += 1

        logger.info(f'variable_to_atom after first pass: {self.variable_to_atom}')
        self.helper_counter = 0
        new_body = []

        for stmt in node.body:
            if (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)) or \
               (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):

                call_node = stmt.value if isinstance(stmt, ast.Expr) else stmt.value
                component_type = getattr(call_node.func, 'id', 'component')
                callsite_hint = f"{self.filename}:{getattr(call_node, 'lineno', 0)}"
                component_id = generate_stable_id(component_type, callsite_hint=callsite_hint)
                stable_name = generate_stable_atom_id_from_component_id(component_id)

                logger.info(f"second pass - stable_name: {stable_name}")

                deps = []
                for arg in call_node.args:
                    if isinstance(arg, ast.Name):
                        var = arg.id
                        if var in self.variable_to_atom:
                            deps.append(self.variable_to_atom[var])
                    elif isinstance(arg, ast.JoinedStr):
                        for value in arg.values:
                            if isinstance(value.value, ast.Name):
                                var = value.value.id
                                if var in self.variable_to_atom:
                                    deps.append(self.variable_to_atom[var])

                for kw in call_node.keywords:
                    if isinstance(kw.value, ast.Name):
                        var = kw.value.id
                        if var in self.variable_to_atom:
                            deps.append(self.variable_to_atom[var])

                param_mapping = {}
                sorted_deps = sorted(deps)
                for idx, dep in enumerate(sorted_deps):
                    param_name = f"param{idx}"
                    param_mapping[dep] = param_name

                keywords = [
                    ast.keyword(arg="name", value=ast.Constant(value=stable_name))
                ]

                if deps:
                    keywords.append(
                        ast.keyword(
                            arg="dependencies",
                            value=ast.List(
                                elts=[ast.Constant(value=dep) for dep in sorted_deps],
                                ctx=ast.Load(),
                            ),
                        )
                    )

                decorator = ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="workflow", ctx=ast.Load()),
                        attr="atom",
                        ctx=ast.Load(),
                    ),
                    args=[],
                    keywords=keywords,
                )

                args_ast = ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=param_mapping[dep]) for dep in sorted_deps],
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[],
                )

                if self._should_inject_callsite_hint(call_node) and not self._has_callsite_hint(call_node):
                    call_node.keywords.append(
                        ast.keyword(arg="callsite_hint", value=ast.Constant(value=callsite_hint))
                    )

                new_call = ast.fix_missing_locations(
                    self._replace_dep_args(call_node, param_mapping)
                )
                body_ast = [ast.Return(value=new_call)]
                func_name = f"_auto_atom_{self.helper_counter}"
                func_def = ast.FunctionDef(
                    name=func_name,
                    args=args_ast,
                    body=body_ast,
                    decorator_list=[decorator],
                    returns=None,
                    type_comment=None,
                )
                func_def.generated_atom_name = stable_name
                self.atoms.append(stable_name)
                self.generated_helpers.append(func_def)

                call_args = []
                for dep in sorted_deps:
                    var_name = next((var for var, atom in self.variable_to_atom.items() if atom == dep), None)
                    if var_name:
                        call_args.append(ast.Name(id=var_name, ctx=ast.Load()))
                        logger.info(f"Calling {func_name} with positional arg from variable: {var_name} for dependency: {dep}")
                    else:
                        call_args.append(ast.Constant(value=None))
                        logger.warning(f"Dependency {dep} could not be resolved to a variable; using None")

                new_call_expr = ast.Call(
                    func=ast.Name(id=func_name, ctx=ast.Load()),
                    args=call_args,
                    keywords=[],
                )

                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            self.variable_to_atom[target.id] = stable_name
                    new_stmt = ast.Assign(targets=stmt.targets, value=new_call_expr)
                else:
                    new_stmt = ast.Expr(value=new_call_expr)

                new_body.append(func_def)
                new_body.append(new_stmt)
                self.helper_counter += 1
            else:
                new_body.append(stmt)

        node.body = new_body
        self.generic_visit(node)
        return node

    def _replace_dep_args(self, call_node, param_mapping):
        def replace_name(name):
            mapped = param_mapping.get(self.variable_to_atom.get(name.id))
            return ast.Name(id=mapped if mapped else name.id, ctx=ast.Load())

        def replace_kw(value):
            if isinstance(value, ast.Name):
                return replace_name(value)
            elif isinstance(value, ast.JoinedStr):
                return self._replace_formatted_value(value, param_mapping)
            return value

        new_call = ast.Call(
            func=call_node.func,
            args=[replace_kw(arg) for arg in call_node.args],
            keywords=[
                ast.keyword(arg=kw.arg, value=replace_kw(kw.value)) for kw in call_node.keywords
            ],
        )
        return new_call

    def _replace_formatted_value(self, joined_str, param_mapping):
        if isinstance(joined_str, ast.JoinedStr):
            new_values = []
            for value in joined_str.values:
                if isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name):
                    atom_name = self.variable_to_atom.get(value.value.id)
                    if atom_name and atom_name in param_mapping:
                        value.value = ast.Name(id=param_mapping[atom_name], ctx=ast.Load())
                new_values.append(value)
            return ast.JoinedStr(values=new_values)
        return joined_str

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
            for fn in self._all_function_defs:
                if fn.name == callee_name and hasattr(fn, "generated_atom_name"):
                    callee_atom = fn.generated_atom_name
                    caller_atom = getattr(self.current_function, "generated_atom_name", None)
                    if caller_atom and callee_atom:
                        self.dependencies.setdefault(caller_atom, set()).add(callee_atom)
            if callee_name in self.variable_to_atom:
                callee_atom = self.variable_to_atom[callee_name]
                caller_atom = getattr(self.current_function, "generated_atom_name", None)
                if caller_atom and callee_atom:
                    self.dependencies.setdefault(caller_atom, set()).add(callee_atom)

        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if self._is_top_level(node):
            callsite_hint = f"{self.filename}:{getattr(node, 'lineno', 0)}"
            stable_name = generate_stable_id("_auto_atom", callsite_hint=callsite_hint)
            decorator = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="workflow", ctx=ast.Load()),
                    attr="atom",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value=stable_name))
                ],
            )
            node.decorator_list.insert(0, decorator)
            node.generated_atom_name = stable_name
            self.atoms.append(stable_name)

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
                        isinstance(decorator, ast.Call) and
                        isinstance(decorator.func, ast.Attribute) and
                        decorator.func.attr == "atom"
                    ):
                        existing_keys = {kw.arg for kw in decorator.keywords}
                        if "dependencies" not in existing_keys:
                            sorted_deps = sorted(deps)
                            decorator.keywords.append(
                                ast.keyword(
                                    arg="dependencies",
                                    value=ast.List(
                                        elts=[ast.Constant(value=dep) for dep in sorted_deps],
                                        ctx=ast.Load()
                                    )
                                )
                            )

        return node

    def _is_top_level(self, node):
        return isinstance(getattr(node, "parent", None), ast.Module)


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
    return new_tree, transformer.atoms
