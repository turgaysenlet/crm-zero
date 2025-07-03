import logging
from typing import List

from src.core.access.access_rule import AccessRule
from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("Profile")
logger.setLevel(logging.DEBUG)


class Profile(DataObject):
    name: str
    access_rules: List[AccessRule] = []

    @classmethod
    def get_custom_fields(cls) -> List[DataField]:
        return []

    def __init__(self, **data):
        super().__init__(id=data["id"],
                         name=data["name"],
                         access_rules=data["access_rules"],
                         fields=Profile.get_custom_fields())
        logger.debug(f"Creating profile: {self}")
