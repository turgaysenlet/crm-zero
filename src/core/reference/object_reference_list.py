import logging
from typing import List

from pydantic import BaseModel

logging.basicConfig()
logger = logging.getLogger("ObjectReferenceList")
logger.setLevel(logging.DEBUG)


class ObjectReferenceList(BaseModel):
    object_type_name: str
    object_ids: List[str]

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"Creating object reference list: {self}")
