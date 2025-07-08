from typing import Optional

from pydantic import BaseModel

from src.core.objects.case import Case
from src.core.reference.object_reference import ObjectReference


class CaseCreateRequestApiRecord(BaseModel):
    owner_id: str
    account_id: str
    summary: str
    description: Optional[str] = None

    def create_case(self) -> Case:
        return Case(owner_id=ObjectReference.from_type_and_id("User", self.owner_id),
                    account_id=ObjectReference.from_type_and_id("Account", self.account_id),
                    summary=self.summary,
                    description=self.description)
