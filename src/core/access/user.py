import logging
from typing import List

from src.core.access.profile import Profile
from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("User")
logger.setLevel(logging.DEBUG)


class User(DataObject):
    username: str
    fullname: str
    password_hash: str
    profiles: List[Profile] = []

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(username=data["username"],
                         fullname=data["fullname"],
                         password_hash=data.get("password_hash", ""),
                         profiles=data["profiles"],
                         fields=User.get_custom_fields())
        logger.debug(f"Creating user: {self}")
