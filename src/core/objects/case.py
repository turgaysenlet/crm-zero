import logging
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
        # Increment the case number before creating a new case
        Case.last_case_number += 1
        try:
            super().__init__(id=data["id"],
                             case_number=Case.case_number_from_number(Case.last_case_number),
                             owner_id=data["owner_id"],
                             account_id=data["account_id"],
                             summary=data["summary"],
                             description=data.get("description", ""),
                             fields=Case.get_custom_fields())
            logger.debug(f"Creating case: {self}")
        except Exception as e:
            # Decrement back to orginal if creation failed.
            Case.last_case_number -= 1
            logger.error(f"Error creating case: {str(e)}")
