from enum import Enum


class Status(Enum):
    ALIVE = 1
    DEAD = 0

    @property
    def label(self):
        match self:
            case 1:
                return "vivant"
            case 0:
                return "mort"
            case _:
                return "état non trouvé"
