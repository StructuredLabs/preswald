class ComponentReturn:
    """
    Wrapper for component return values that separates the visible return
    value from the internal component metadata (e.g. for render tracking).
    """

    def __init__(self, value, component):
        self.value = value
        self._preswald_component = component

    def __str__(self): return str(self.value)
    def __float__(self): return float(self.value)
    def __bool__(self): return bool(self.value)
    def __repr__(self): return repr(self.value)
