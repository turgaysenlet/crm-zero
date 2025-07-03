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

