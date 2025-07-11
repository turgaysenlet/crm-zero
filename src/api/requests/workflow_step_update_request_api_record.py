import logging
import time
import uuid
from typing import Dict

from pydantic import BaseModel

from src.core.eventbus.workflow_step import WorkflowStep
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("WorkflowStepUpdateRequestApiRecord")
logger.setLevel(logging.DEBUG)


class WorkflowStepUpdateRequestApiRecord(BaseModel):
    id: str
    workflow_step_name: str
    workflow_step_code: str

    def update_workflow_step(self, workflow_step: WorkflowStep):
        if self.workflow_step_name != "":
            workflow_step.workflow_step_name = self.workflow_step_name
        if self.workflow_step_code != "":
            workflow_step.workflow_step_code = self.workflow_step_code
