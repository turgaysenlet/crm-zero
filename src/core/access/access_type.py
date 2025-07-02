from enum import Flag, auto


class AccessType(Flag):
    NONE = 0
    CREATE = auto()
    READ = auto()
    WRITE = auto()
    DELETE = auto()

    def __str__(self):
        return "|".join(flag.name.lower() for flag in AccessType if flag in self and flag != AccessType.NONE)

    def to_db(self) -> str:
        return str(self)

    @classmethod
    def from_str(cls, value: str) -> 'AccessType':
        if not value or value.lower() == "none":
            return cls.NONE
        parts = value.lower().split("|")
        result = cls.NONE
        for part in parts:
            try:
                result |= cls[part.upper()]
            except KeyError:
                raise ValueError(f"Invalid access flag: {part}")
        return result
