from preswald.interfaces.dependency_tracker import track_dependency, get_current_context

class TrackedValue:
    """Wraps a value and tracks accesses for reactive recomputation."""

    def __init__(self, value, atom_name):
        self._value = value
        self._atom_name = atom_name

    @property
    def value(self):
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
        return f"{self.__class__.__name__}({repr(self._value)})"

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
