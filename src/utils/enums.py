from enum import IntEnum


class ChoiceEnum(IntEnum):
    """Base enum class for int fields."""

    @classmethod
    def choices(cls, with_unknown=True):
        """Return list of choices."""
        result = tuple((i.value, i.name) for i in cls)
        if with_unknown:
            result += ((None, 'UNKNOWN'),)
        return result

    @classmethod
    def from_string(cls, country_name: str):
        """Convert string to enum member."""
        for member in cls:
            if member.name.lower() == country_name.lower().replace(' ', '_'):
                return member
        raise ValueError(f'Country "{country_name}" not found in Countries.')


class Country(ChoiceEnum):
    """List of countries."""

    SPAIN = 0
    ENGLAND = 1
    FRANCE = 2
    GERMANY = 3
    ITALY = 4
    USA = 5
    TURKEY = 6
    PORTUGAL = 7
    SAUDI_ARABIA = 8
    SOUTH_AMERICA = 9
    NETHERLANDS = 10
    ARGENTINA = 11
    BELGIUM = 12
    SCOTLAND = 13
    DENMARK = 14
    AUSTRIA = 15
    SWITZERLAND = 16
    POLAND = 17
    SOUTH_KOREA = 18
    SWEDEN = 19
    NORWAY = 20
    CHINA = 21
    ROMANIA = 22
    AUSTRALIA = 23
    INDIA = 24
    REPUBLIC_OF_IRELAND = 25

    def get_readable_name(self) -> str:
        """Return readable name."""
        return self.name.replace('_', ' ').title()


class FIFAVersion(ChoiceEnum):
    """List of FIFA versions."""

    FIFA21 = 21
    FIFA22 = 22
    FIFA23 = 23
    FIFA24 = 24
    FIFA25 = 25
