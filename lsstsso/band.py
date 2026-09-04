from enum import Enum


class Band(Enum):
    u = 0
    g = 1
    r = 2
    i = 3
    z = 4
    y = 5

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __repr__(self):
        return f"<Band: {str(self)}>"

    def __str__(self):
        return self.name
