import logging
import uuid
from typing import List, Optional, ClassVar

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("Case")
logger.setLevel(logging.DEBUG)


class Case(DataObject):
    case_number: str
    owner_id: ObjectReference
    account_id: ObjectReference
    summary: str
    description: Optional[str] = None
    last_case_number: ClassVar[int] = 0

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    @classmethod
    def case_number_from_number(cls, number: int) -> str:
        return f"{number:08d}"

    def __init__(self, **data):
        existing_case: bool = data.__contains__("id")
        if existing_case:
            case_number = data["case_number"]
        else:
            # Increment the case number before creating a new case
            Case.last_case_number += 1
            case_number = Case.case_number_from_number(Case.last_case_number)
        try:
            super().__init__(id=data.get("id", uuid.uuid4()),
                             case_number=case_number,
                             owner_id=data["owner_id"],
                             account_id=data["account_id"],
                             summary=data["summary"],
                             description=data.get("description", ""),
                             custom_fields=Case.get_custom_fields(),
                             object_type_name="Case")
            logger.debug(f"Creating case: {self}")
        except Exception as e:
            logger.error(f"Error creating case: {str(e)}")
