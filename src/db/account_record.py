import logging
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.core.objects.account import Account

logging.basicConfig()
logger = logging.getLogger("AccountRecord")
logger.setLevel(logging.DEBUG)


class AccountRecord(BaseModel):
    id: str
    account_number: str
    owner_id: str
    account_name: str
    description: Optional[str] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0

    @classmethod
    def table_name(cls) -> str:
        return "Accounts"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{AccountRecord.table_name()} (
                id TEXT PRIMARY KEY,
                account_number TEXT UNIQUE NOT NULL,
                owner_id TEXT NOT NULL,
                account_name TEXT NOT NULL,                
                description TEXT,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT             
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, account_number, owner_id, account_name, description, created_at, updated_at, commit_at'

    @classmethod
    def get_last_account_number_query(cls) -> str:
        query = f"SELECT MAX(CAST(account_number AS INTEGER)) AS max_account_number FROM {AccountRecord.table_name()}"
        return query

    @classmethod
    def from_object(cls, obj: Account) -> "AccountRecord":
        return AccountRecord(
            id=str(obj.id),
            account_number=obj.account_number,
            owner_id=str(obj.owner_id),
            account_name=obj.account_name,
            description=obj.description,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at)

    @classmethod
    def from_db_row(cls, row: Dict) -> "AccountRecord":
        return AccountRecord(
            id=row["id"],
            account_number=row["account_number"],
            owner_id=row["owner_id"],
            account_name=row["account_name"],
            description=row.get("description", ""),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            commit_at=row["commit_at"]
        )

    def __init__(self, **data):
        super().__init__(**data)
        now = time.time()
        self.created_at = data.get("created_at", now)
        self.updated_at = data.get("updated_at", now)
        self.commit_at = data.get("commit_at", now)
        logger.debug(f"Creating account record: {self}")

    def insert_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT INTO {AccountRecord.table_name()} ({AccountRecord.table_fields()}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.account_number, self.owner_id, self.account_name, self.description, self.created_at, self.updated_at,
             self.commit_at)
        )
        conn.commit()

    def read_from_db_row(self, row: Dict[str, Any]) -> None:
        self.id = str(row["id"])
        self.account_number = str(row["account_number"])
        self.owner_id = str(row["owner_id"])
        self.account_name = str(row["account_name"])
        self.description = str(row.get("description", ""))
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])

    def read_from_object(self, obj: Account) -> None:
        self.id = str(obj.id)
        self.account_number = obj.account_number
        self.owner_id = obj.owner_id
        self.account_name = obj.account_name
        self.description = obj.description
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at

    def convert_to_object(self) -> Account:
        obj: Account = Account(
            id=uuid.UUID(self.id),
            account_number=self.account_number,
            owner_id=uuid.UUID(self.owner_id),
            account_name=self.account_name,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at
        )
        return obj
