from typing import Optional

from pydantic import BaseModel

from src.core.objects.case import Case
from src.core.objects.case_comment import CaseComment
from src.core.reference.object_reference import ObjectReference


class CaseCreateRequestApiRecord(BaseModel):
    owner_id: str
    case_id: str
    summary: str
    description: Optional[str] = None

    def create_case_comment(self) -> CaseComment:
        return CaseComment(owner_id=ObjectReference.from_type_and_id("User", self.owner_id),
                           case_id=ObjectReference.from_type_and_id("Case", self.case_id),
                           summary=self.summary,
                           description=self.description)
