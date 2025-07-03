import logging

from pydantic import BaseModel

logging.basicConfig()
logger = logging.getLogger("ObjectReference")
logger.setLevel(logging.DEBUG)


class ObjectReference(BaseModel):
    object_type_name: str
    object_id: str

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"Creating object reference: {self}")
