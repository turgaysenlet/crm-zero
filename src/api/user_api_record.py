import logging
import time
import uuid
from typing import Dict

from pydantic import BaseModel

from src.core.access.user import User
from src.core.reference.object_reference_list import ObjectReferenceList

logging.basicConfig()
logger = logging.getLogger("UserApiRecord")
logger.setLevel(logging.DEBUG)


class UserApiRecord(BaseModel):
    id: str
    username: str
    fullname: str
    password_hash: str
    profile_ids: str
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def from_object(cls, obj: User) -> "UserApiRecord":
        profile_ids = "{}"
        if obj.profile_ids is not None:
            profile_ids = obj.profile_ids.to_json_string()
        return UserApiRecord(
            id=str(obj.id),
            username=str(obj.username),
            fullname=obj.fullname,
            password_hash=obj.password_hash,
            profile_ids=profile_ids,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "UserApiRecord":
        return UserApiRecord(
            id=row["id"],
            username=row["username"],
            fullname=row["fullname"],
            password_hash=row["password_hash"],
            profile_ids=row.get("profile_ids", ""),
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
        logger.debug(f"Creating user record: {self}")

    def read_from_object(self, obj: User) -> None:
        profile_ids = "{}"
        if obj.profile_ids is not None:
            profile_ids = obj.profile_ids.to_json_string()
        self.id = str(obj.id)
        self.username = obj.username
        self.fullname = obj.fullname
        self.password_hash = obj.password_hash
        self.profile_ids = profile_ids
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> User:
        obj: User = User(
            id=uuid.UUID(self.id),
            fullname=uuid.UUID(self.owner_id),
            password_hash=self.password_hash,
            profile_ids=ObjectReferenceList.from_string(self.profile_ids),
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
