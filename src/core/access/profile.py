import logging
import uuid
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
        super().__init__(id=data.get("id", uuid.uuid4()),
                         name=data["name"],
                         access_rules=data["access_rules"],
                         custom_fields=Profile.get_custom_fields(),
                         object_type_name="Profile")
        logger.debug(f"Creating profile: {self}")
