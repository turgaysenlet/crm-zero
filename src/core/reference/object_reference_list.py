import logging
import uuid
from typing import List, Optional

from pydantic import BaseModel

from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("ObjectReferenceList")
logger.setLevel(logging.DEBUG)


class ObjectReferenceList(BaseModel):
    object_type_name: str
    object_ids: List[uuid.UUID]

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"Creating object reference list: {self}")

    def to_json_dict(self) -> dict:
        return {
            "object_type_name": self.object_type_name,
            "object_ids": [str(uid) for uid in self.object_ids]
        }

    @classmethod
    def from_list(cls, object_list: List[DataObject]) -> Optional["ObjectReferenceList"]:
        if object_list is None or len(object_list) == 0:
            logger.debug(f"Object list is empty")
            return None
        object_type_name = object_list[0].object_type_name
        ids = [object_item.id for object_item in object_list]
        return ObjectReferenceList(object_type_name=object_type_name, object_ids=ids)
