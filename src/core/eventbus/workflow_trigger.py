import logging
import uuid
from typing import List, ClassVar

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("WorkflowTrigger")
logger.setLevel(logging.DEBUG)


class WorkflowTrigger(DataObject):
    owner_id: ObjectReference
    workflow_trigger_object_type_name: str
    workflow_trigger_event_type: str
    workflow_to_run_id: ObjectReference
    # DO NOT serialize, transient only
    workflows: List[DataObject] = []
    all_workflow_triggers: ClassVar[List["WorkflowTrigger"]] = []

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(id=data.get("id", uuid.uuid4()),
                         owner_id=data["owner_id"],
                         workflow_trigger_object_type_name=data["workflow_trigger_object_type_name"],
                         workflow_trigger_event_type=data["workflow_trigger_event_type"],
                         custom_fields=WorkflowTrigger.get_custom_fields(),
                         workflow_to_run_id=data["workflow_to_run_id"],
                         object_type_name="WorkflowTrigger"
                         )
        logger.debug(f"Creating workflow trigger: {self}")

    def load_workflows_from_all_workflows(self, workflows: List[DataObject]):
        object_ids = [str(self.workflow_to_run_id.object_id)]
        self.workflows = [workflow for workflow in workflows if object_ids.__contains__(str(workflow.id))]

    @classmethod
    def run_matching_triggers(cls, workflow_trigger_object_type_name: str, workflow_trigger_event_type: str,
                              sender_object: DataObject):
        for workflow_trigger in WorkflowTrigger.all_workflow_triggers:
            if workflow_trigger.workflows is not None and \
                    workflow_trigger.workflow_trigger_object_type_name == workflow_trigger_object_type_name and \
                    workflow_trigger.workflow_trigger_event_type == workflow_trigger_event_type:
                for workflow in workflow_trigger.workflows:
                    logger.debug(f"Running workflow: {workflow.workflow_name} for workflow_trigger_object_type_name - {sender_object.id}")
                    workflow.run_workflow(sender_object, workflow_trigger)
