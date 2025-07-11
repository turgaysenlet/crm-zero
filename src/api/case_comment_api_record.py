import logging
import time
import uuid
from typing import Optional, Dict

from pydantic import BaseModel

from src.core.objects.case_comment import CaseComment
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("CaseCommentApiRecord")
logger.setLevel(logging.DEBUG)


class CaseCommentApiRecord(BaseModel):
    id: str
    case_comment_number: str
    owner_id: str
    case_id: str
    summary: str
    description: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def from_object(cls, obj: CaseComment) -> "CaseCommentApiRecord":
        return CaseCommentApiRecord(
            id=str(obj.id),
            case_comment_number=obj.case_comment_number,
            owner_id=obj.owner_id.to_json_str(),
            case_id=obj.case_id.to_json_str(),
            summary=obj.summary,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "CaseCommentApiRecord":
        return CaseCommentApiRecord(
            id=row["id"],
            case_comment_number=row["case_comment_number"],
            owner_id=row["owner_id"],
            case_id=row["case_id"],
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
        logger.debug(f"Creating case comment record: {self}")

    def read_from_object(self, obj: CaseComment) -> None:
        self.id = str(obj.id)
        self.case_comment_number = obj.case_comment_number
        self.owner_id = obj.owner_id.to_json_str()
        self.case_id = obj.case_id.to_json_str()
        self.summary = obj.summary
        self.description = obj.description
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> CaseComment:
        obj: CaseComment = CaseComment(
            id=uuid.UUID(self.id),
            case_comment_number=self.case_comment_number,
            owner_id=ObjectReference.from_json_string(self.owner_id),
            case_id=ObjectReference.from_json_string(self.case_id),
            summary=self.summary,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
