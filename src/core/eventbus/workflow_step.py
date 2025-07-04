import logging
import uuid
from typing import List, ClassVar

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("WorkflowStep")
logger.setLevel(logging.DEBUG)


class WorkflowStep(DataObject):
    owner_id: ObjectReference
    workflow_step_name: str
    workflow_step_code: str
    # DO NOT serialize, transient only
    all_workflow_steps: ClassVar[List["WorkflowStep"]] = []

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(id=data.get("id", uuid.uuid4()),
                         owner_id=data["owner_id"],
                         workflow_step_name=data["workflow_step_name"],
                         workflow_step_code=data["workflow_step_code"],
                         custom_fields=WorkflowStep.get_custom_fields(),
                         object_type_name="WorkflowStep")
        logger.debug(f"Creating workflow step: {self}")
