import logging
import time
import uuid
from typing import List

from pydantic import BaseModel, Field

from src.core.base.data_field import DataField

logging.basicConfig()
logger = logging.getLogger("DataObject")
logger.setLevel(logging.DEBUG)


class DataObject(BaseModel):
    # TODO: Find a way to remove duplicate UUID creation for base class
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0
    custom_fields: List[DataField] = []
    # Retrieving dynamic type name in Pydantic subclasses is problematic, storing the individual object type name in
    # instances and the database instead.
    object_type_name: str

    def __init__(self, **data):
        super().__init__(**data)
        now = time.time()
        self.created_at = data.get("created_at", now)
        self.updated_at = data.get("updated_at", now)
        self.commit_at = data.get("commit_at", now)
        logger.debug(f"Creating data object: {self} for {self.__class__.__name__} class")
