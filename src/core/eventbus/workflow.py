import logging
import uuid
from typing import List, Optional

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.eventbus.workflow_step import WorkflowStep
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList

logging.basicConfig()
logger = logging.getLogger("Workflow")
logger.setLevel(logging.DEBUG)


class Workflow(DataObject):
    owner_id: ObjectReference
    workflow_name: str
    workflow_step_ids: Optional[ObjectReferenceList] = None
    # DO NOT serialize, transient only
    workflow_steps: List[WorkflowStep] = []

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(id=data.get("id", uuid.uuid4()),
                         owner_id=data["owner_id"],
                         workflow_name=data["workflow_name"],
                         workflow_step_ids=data["workflow_step_ids"],
                         custom_fields=Workflow.get_custom_fields(),
                         object_type_name="Workflow")
        logger.debug(f"Creating workflow: {self}")

    def load_steps(self, workflow_steps: List[WorkflowStep]):
        self.workflow_steps = workflow_steps

    def run_workflow(self):
        sender = "1234"
        print(f"-Running workflow '{self.workflow_name}' with id '{str(self.id)}'...")
        for workflow_step in self.workflow_steps:
            print(f"---Running step '{workflow_step.workflow_step_name}' with id '{str(workflow_step.id)}'...")
            exec(workflow_step.workflow_step_code, {}, locals())
            print(f"---Done running step '{workflow_step.workflow_step_name}' with id '{str(workflow_step.id)}'.")
        print(f"-Done running workflow '{self.workflow_name}' with id '{str(self.id)}'.")
