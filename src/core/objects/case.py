import logging
from typing import List, Optional, ClassVar

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("Case")
logger.setLevel(logging.DEBUG)


class Case(DataObject):
    case_number: str
    owner_id: str
    summary: str
    description: Optional[str] = None
    last_case_number: ClassVar[int] = 0

    @classmethod
    def get_fields(cls) -> List[DataField]:
        return []

    @classmethod
    def case_number_from_number(cls, number: int) -> str:
        return f"{number:08d}"

    def __init__(self, **data):
        Case.last_case_number += 1
        super().__init__(case_number=Case.case_number_from_number(Case.last_case_number),
                         owner_id=data["owner_id"],
                         summary=data["summary"],
                         description=data.get("description", ""),
                         fields=Case.get_fields())
        logger.debug(f"Creating case: {self}")
