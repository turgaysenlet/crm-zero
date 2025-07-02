import logging
from typing import List, Optional

from src.core.base.data_field import DataField
from src.core.base.data_object import DataObject

logging.basicConfig()
logger = logging.getLogger("Account")
logger.setLevel(logging.DEBUG)


class Account(DataObject):
    account_number: str
    owner_id: str
    name: str

    def __init__(self, **data):
        super().__init__(name="Account",
                         api_name="account",
                         description="Account")
        logger.debug(f"Creating account: {self}")
