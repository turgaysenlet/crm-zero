import json
import logging
import uuid
from typing import Optional

from pydantic import BaseModel

from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("ObjectReference")
logger.setLevel(logging.DEBUG)


class ObjectReference(BaseModel):
    object_type_name: str
    object_id: uuid.UUID

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"Creating object reference: {self}")

    @classmethod
    def from_object(cls, data_object: DataObject) -> Optional["ObjectReference"]:
        return ObjectReference(object_type_name=data_object.object_type_name, object_id=data_object.id)

    @classmethod
    def from_json_string(cls, json_str: str) -> Optional["ObjectReference"]:
        j = json.loads(json_str or {})
        return ObjectReference(object_type_name=j["object_type_name"], object_id=uuid.UUID(j["object_id"]))

    def to_json_str(self) -> str:
        di = self.dict()
        new_dict = {}
        for (k, v) in di.items():
            # Only fix UUID, since it is not serializable
            # Do not stringify numbers
            if isinstance(v, uuid.UUID):
                v = str(v)
            new_dict[k] = v
        return json.dumps(new_dict)

