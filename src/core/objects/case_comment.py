import logging
import uuid
from typing import List, Optional, ClassVar

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.eventbus.workflow_trigger import WorkflowTrigger
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("CaseComment")
logger.setLevel(logging.DEBUG)


class CaseComment(DataObject):
    case_comment_number: str
    owner_id: ObjectReference
    case_id: ObjectReference
    summary: str
    description: Optional[str] = None

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    @classmethod
    def case_comment_number_from_number(cls, number: int) -> str:
        return f"{number:08d}"

    def __init__(self, **data):
        existing_case_comment: bool = data.__contains__("id")
        if existing_case_comment:
            case_comment_number = data["case_comment_number"]
        else:
            # Increment the case comment number before creating a new case number
            case_comment_number = CaseComment.case_comment_number_from_number(1)
        try:
            super().__init__(id=data.get("id", uuid.uuid4()),
                             case_comment_number=case_comment_number,
                             owner_id=data["owner_id"],
                             case_id=data["case_id"],
                             summary=data["summary"],
                             description=data.get("description", ""),
                             custom_fields=CaseComment.get_custom_fields(),
                             object_type_name="CaseComment")
            logger.debug(f"Creating case comment: {self}")
            logger.debug(f"Running case comment triggers: {self.id}")
            # Run triggers only when the case comment is brand new, not a copy of an existing case comment
            # TODO: Run triggers ar database commit time
            if not existing_case_comment:
                WorkflowTrigger.run_matching_triggers("CaseComment", "CREATE", self)
            logger.debug(f"Done running case comment triggers: {self.id}")
        except Exception as e:
            logger.error(f"Error creating case comment: {str(e)}")

    def __str__(self):
        return self.model_dump_json(indent=2)

