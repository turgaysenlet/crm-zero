import uuid
import logging
from typing import Optional, ClassVar

from pydantic import BaseModel

from src.core.base.field_type import FieldType

logging.basicConfig()
logger = logging.getLogger("Data Field")
logger.setLevel(logging.DEBUG)


class DataField(BaseModel):
    name: str
    api_name: str
    field_type: FieldType
    count: ClassVar[int] = 0

    def __init__(self, **data):
        super().__init__(**data)
        type(self).count += 1
        logger.debug(f"Creating data field: {self} for {self.__class__.__name__} class")
