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

    FIFA21 = 21
    FIFA22 = 22
    FIFA23 = 23
    FIFA24 = 24
    FIFA25 = 25
