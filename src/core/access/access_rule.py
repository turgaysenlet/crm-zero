import logging
import uuid

from src.core.access.access_type import AccessType
from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("AccessRule")
logger.setLevel(logging.DEBUG)


class AccessRule(DataObject):
    data_object_type: str
    access_type: AccessType

    # TODO: Add field based access rules to AccessRule.

    def __init__(self, **data):
        super().__init__(id=data.get("id", uuid.uuid4()),
                         data_object_type=data["data_object_type"],
                         access_type=data["access_type"],
                         object_type_name="AccessRule"
                         )
        logger.debug(f"Creating access rule: {self}")

    def to_json_dict(self) -> dict:
        di = self.dict()
        new_dict = {}
        for (k, v) in di.items():
            # Only fix UUID, since it is not serializable
            # Do not stringify numbers
            if isinstance(v, uuid.UUID):
                v = str(v)
            elif isinstance(v, AccessType):
                v = str(v)
            new_dict[k] = v
        return new_dict

    @classmethod
    def from_json_dict(cls, json_dict) -> "AccessRule":
        return AccessRule(
            id=uuid.UUID(json_dict["id"]),
            data_object_type=json_dict["data_object_type"],
            access_type=AccessType.from_str(json_dict["access_type"]),
            created_at=json_dict["created_at"],
            updated_at=json_dict["updated_at"],
            commit_at=json_dict["commit_at"]
        )

    @classmethod
    def object_type_accessible_to_all(cls, object_type: str) -> bool:
        return ["User", "Profile", "Workflow", "WorkflowStep", "WorkflowTrigger"].__contains__(object_type)
