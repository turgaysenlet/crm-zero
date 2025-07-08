from typing import Optional

from pydantic import BaseModel

from src.core.objects.account import Account
from src.core.reference.object_reference import ObjectReference


class AccountCreateRequestApiRecord(BaseModel):
    owner_id: str
    account_name: str
    description: Optional[str] = None

    def create_account(self) -> Account:
        return Account(owner_id=ObjectReference.from_type_and_id("User", self.owner_id),
                       account_name=self.account_name,
                       description=self.description)
