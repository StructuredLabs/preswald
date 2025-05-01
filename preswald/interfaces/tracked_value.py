import logging

from preswald.interfaces.dependency_tracker import track_dependency


logger = logging.getLogger(__name__)


class TrackedValue:
    """
    Wraps a value and automatically tracks read access for reactive dependency resolution.

    When a value is read (via property access or coercion), we register a dynamic dependency
    from the current executing atom to the atom that produced this value.
    """

    def __init__(self, value, atom_name):
        self._value = value
        self._atom_name = atom_name
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[Dependency Tracking] Created TrackedValue {self._value=} {self._atom_name=}")
        else:
            logger.info(f"[Dependency Tracking] Created TrackedValue {self._atom_name=}")

    @property
    def value(self):
        # Track dynamic access to the value
        track_dependency(self._atom_name)
        return self._value

    def __format__(self, fmt):
        track_dependency(self._atom_name)
        return format(self.value, fmt)

    def __int__(self):
        track_dependency(self._atom_name)
        return int(self.value)

    def __repr__(self):
        track_dependency(self._atom_name)
        return f"{self.__class__.__name__}({self._value!r})"

    def __str__(self):
        track_dependency(self._atom_name)
        return str(self.value)

    def __le__(self, other):
        track_dependency(self._atom_name)
        return self.value <= other

    def __lt__(self, other):
        track_dependency(self._atom_name)
        return self.value < other

    def __ge__(self, other):
        track_dependency(self._atom_name)
        return self.value >= other

    def __gt__(self, other):
        track_dependency(self._atom_name)
        return self.value > other

    def __eq__(self, other):
        track_dependency(self._atom_name)
        return self.value == other

    def __ne__(self, other):
        track_dependency(self._atom_name)
        return self.value != other
