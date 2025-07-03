import logging
from typing import List

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject
from src.core.reference.object_reference import ObjectReference

logging.basicConfig()
logger = logging.getLogger("User")
logger.setLevel(logging.DEBUG)


class User(DataObject):
    username: str
    fullname: str
    password_hash: str
    profiles: List[ObjectReference] = []

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(id=data["id"],
                         username=data["username"],
                         fullname=data["fullname"],
                         password_hash=data.get("password_hash", ""),
                         profiles=data["profiles"],
                         fields=User.get_custom_fields())
        logger.debug(f"Creating user: {self}")
