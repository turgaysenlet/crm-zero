import logging
import time
import uuid
from typing import Optional, Dict

from pydantic import BaseModel

from src.core.objects.account import Account

logging.basicConfig()
logger = logging.getLogger("AccountApiRecord")
logger.setLevel(logging.DEBUG)


class AccountApiRecord(BaseModel):
    id: str
    account_number: str
    owner_id: str
    account_name: str
    description: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def from_object(cls, obj: Account) -> "AccountApiRecord":
        return AccountApiRecord(
            id=str(obj.id),
            account_number=obj.account_number,
            owner_id=str(obj.owner_id),
            account_name=obj.account_name,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "AccountApiRecord":
        return AccountApiRecord(
            id=row["id"],
            account_number=row["account_number"],
            owner_id=row["owner_id"],
            account_name=row["account_name"],
            description=row.get("description", ""),
            created_at=float(row["created_at"]),
            updated_at=float(row["updated_at"]),
            commit_at=float(row["commit_at"]),
            object_type_name=row["object_type_name"]
        )

    def __init__(self, **data):
        super().__init__(**data)
        now = time.time()
        self.created_at = data.get("created_at", now)
        self.updated_at = data.get("updated_at", now)
        self.commit_at = data.get("commit_at", now)
        logger.debug(f"Creating account record: {self}")

    def read_from_object(self, obj: Account):
        self.id = str(obj.id)
        self.account_number = obj.account_number
        self.owner_id = str(obj.owner_id),
        self.account_name = obj.account_name
        self.description = obj.description
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> Account:
        obj: Account = Account(
            id=uuid.UUID(self.id),
            account_number=self.account_number,
            owner_id=uuid.UUID(self.owner_id),
            account_name=self.account_name,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
