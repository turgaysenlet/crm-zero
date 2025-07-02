from enum import Enum


class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    PICKLIST = "picklist"
    LOOKUP = "lookup"
