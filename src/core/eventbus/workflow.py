import logging
import uuid
from typing import List, Optional

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList

logging.basicConfig()
logger = logging.getLogger("Workflow")
logger.setLevel(logging.DEBUG)


class Workflow(DataObject):
    owner_id: ObjectReference
    workflow_name: str
    workflow_step_ids: Optional[ObjectReferenceList] = None

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
