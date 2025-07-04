import logging
import uuid
from typing import List, Optional

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference_list import ObjectReferenceList

logging.basicConfig()
logger = logging.getLogger("User")
logger.setLevel(logging.DEBUG)


class User(DataObject):
    username: str
    fullname: str
    password_hash: str
    profile_ids: Optional[ObjectReferenceList] = None

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(id=data.get("id", uuid.uuid4()),
                         username=data["username"],
                         fullname=data["fullname"],
                         password_hash=data.get("password_hash", ""),
                         profile_ids=data["profile_ids"],
                         custom_fields=User.get_custom_fields(),
                         object_type_name="User")
        logger.debug(f"Creating user: {self}")
