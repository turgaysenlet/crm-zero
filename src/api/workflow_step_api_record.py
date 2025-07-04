import logging
import time
import uuid
from typing import Dict

from pydantic import BaseModel

from src.core.eventbus.workflow_step import WorkflowStep
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("WorkflowStepApiRecord")
logger.setLevel(logging.DEBUG)


class WorkflowStepApiRecord(BaseModel):
    id: str
    owner_id: str
    workflow_step_name: str
    workflow_step_code: str
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    object_type_name: str

    @classmethod
    def from_object(cls, obj: WorkflowStep) -> "WorkflowStepApiRecord":
        return WorkflowStepApiRecord(
            id=str(obj.id),
            owner_id=obj.owner_id.to_json_str(),
            workflow_step_name=str(obj.workflow_step_name),
            workflow_step_code=obj.workflow_step_code,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at,
            object_type_name=obj.object_type_name
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "WorkflowStepApiRecord":
        return WorkflowStepApiRecord(
            id=row["id"],
            owner_id=row["owner_id"],
            workflow_step_name=row["workflow_step_name"],
            workflow_step_code=row.get("workflow_step_code", ""),
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
        logger.debug(f"Creating workflow step record: {self}")

    def read_from_object(self, obj: WorkflowStep) -> None:
        self.id = str(obj.id)
        self.owner_id = obj.owner_id.to_json_str()
        self.workflow_step_name = obj.workflow_step_name
        self.workflow_step_code = obj.workflow_step_code
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at
        self.object_type_name = obj.object_type_name

    def convert_to_object(self) -> WorkflowStep:
        obj: WorkflowStep = WorkflowStep(
            id=uuid.UUID(self.id),
            owner_id=ObjectReference.from_json_string(self.owner_id),
            workflow_step_code=self.workflow_step_code,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at,
            object_type_name=self.object_type_name
        )
        return obj
