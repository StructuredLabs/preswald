class FrameContext:
    def __init__(self):
        self.variable_to_atom: dict[str, str] = {}
        self.generated_atoms: list[ast.FunctionDef] = []
        self.stmt_variable_maps = {}
        self.tuple_variable_index: dict[str, int] = {}
        self.tuple_unpacked_names = {}
        self.tuple_returning_atoms: set[str] = set()
        self.atom_return_types: dict[str, str] = {}
