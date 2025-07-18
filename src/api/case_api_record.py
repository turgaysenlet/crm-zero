import logging
import time
import uuid
from typing import Optional, Dict

from pydantic import BaseModel

from src.core.objects.case import Case
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("CaseApiRecord")
logger.setLevel(logging.DEBUG)


class CaseApiRecord(BaseModel):
    id: str
    case_number: str
    owner_id: str
    account_id: str
    summary: str
    description: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def from_object(cls, obj: Case) -> "CaseApiRecord":
        return CaseApiRecord(
            id=str(obj.id),
            case_number=obj.case_number,
            owner_id=obj.owner_id.to_json_str(),
            account_id=obj.account_id.to_json_str(),
            summary=obj.summary,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "CaseApiRecord":
        return CaseApiRecord(
            id=row["id"],
            case_number=row["case_number"],
            owner_id=row["owner_id"],
            account_id=row["account_id"],
            summary=row["summary"],
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
        logger.debug(f"Creating case record: {self}")

    def read_from_object(self, obj: Case) -> None:
        self.id = str(obj.id)
        self.case_number = obj.case_number
        self.owner_id = obj.owner_id.to_json_str()
        self.account_id = obj.account_id.to_json_str()
        self.summary = obj.summary
        self.description = obj.description
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> Case:
        obj: Case = Case(
            id=uuid.UUID(self.id),
            case_number=self.case_number,
            owner_id=ObjectReference.from_json_string(self.owner_id),
            account_id=ObjectReference.from_json_string(self.account_id),
            summary=self.summary,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
