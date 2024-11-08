from enum import IntEnum


class BaseFieldEnum(IntEnum):
    """Base enum class for int fields."""

    @classmethod
    def choices(cls):
        """Return list of choices."""
        return tuple((i.name, i.value) for i in cls)


class Countries(BaseFieldEnum):
    """List of countries."""

    ENGLAND = 0


class FIFAVersion(BaseFieldEnum):
    """List of FIFA versions."""

    FIFA21 = 0
    FIFA22 = 1
    FIFA23 = 2
    FIFA24 = 3
    FIFA25 = 4
