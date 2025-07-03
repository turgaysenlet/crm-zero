import logging
import uuid
from typing import List, Optional, ClassVar

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("Account")
logger.setLevel(logging.DEBUG)


class Account(DataObject):
    account_number: str
    owner_id: ObjectReference
    account_name: str
    description: Optional[str] = None
    last_account_number: ClassVar[int] = 0

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    @classmethod
    def account_number_from_number(cls, number: int) -> str:
        return f"{number:08d}"

    def __init__(self, **data):
        # Increment the account number before creating a new account
        Account.last_account_number += 1
        super().__init__(id=data.get("id", uuid.uuid4()),
                         account_number=Account.account_number_from_number(Account.last_account_number),
                         owner_id=data["owner_id"],
                         account_name=data["account_name"],
                         description=data.get("description", ""),
                         custom_fields=Account.get_custom_fields(),
                         object_type_name="Account")
        logger.debug(f"Creating account: {self}")
