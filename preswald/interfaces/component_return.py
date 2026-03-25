from typing import Any


class ComponentReturn:
    """
    Wrapper for component return values that separates the visible return
    value from the internal component metadata (e.g. for render tracking).
    """

    value: Any
    _preswald_component: dict[str, Any]

    def __init__(self, value: Any, component: dict[str, Any]) -> None:
        self.value = value
        self._preswald_component = component

    def __str__(self) -> str: return str(self.value)
    def __float__(self) -> float: return float(self.value)
    def __bool__(self) -> bool: return bool(self.value)
    def __repr__(self) -> str: return repr(self.value)
