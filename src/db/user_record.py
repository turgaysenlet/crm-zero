import json
import logging
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Dict, Any

from pydantic import BaseModel

from src.core.access.user import User
from src.db.profile_record import ProfileRecord

logging.basicConfig()
logger = logging.getLogger("UserRecord")
logger.setLevel(logging.DEBUG)


class UserRecord(BaseModel):
    id: str
    username: str
    fullname: str
    password_hash: str
    profiles: str
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0

    @classmethod
    def table_name(cls) -> str:
        return "Users"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{UserRecord.table_name()} (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                fullname TEXT NOT NULL,
                password_hash TEXT NOT NULL,                
                profiles TEXT,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT             
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, username, fullname, password_hash, profiles, created_at, updated_at, commit_at'

    @classmethod
    def from_object(cls, obj: User) -> "UserRecord":
        return UserRecord(
            id=str(obj.id),
            username=str(obj.username),
            fullname=obj.fullname,
            password_hash=obj.password_hash,
            profiles=json.dumps([ProfileRecord.from_object(profile).dict() for profile in obj.profiles]),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "UserRecord":
        return UserRecord(
            id=row["id"],
            username=row["username"],
            fullname=row["fullname"],
            password_hash=row["password_hash"],
            profiles=row.get("profiles", ""),
            created_at=float(row["created_at"]),
            updated_at=float(row["updated_at"]),
            commit_at=float(row["commit_at"])
        )

    def __init__(self, **data):
        super().__init__(**data)
        now = time.time()
        self.created_at = data.get("created_at", now)
        self.updated_at = data.get("updated_at", now)
        self.commit_at = data.get("commit_at", now)
        logger.debug(f"Creating user record: {self}")

    def insert_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT INTO {UserRecord.table_name()} ({UserRecord.table_fields()}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.username, self.fullname, self.password_hash, self.profiles, self.created_at, self.updated_at,
             self.commit_at)
        )
        conn.commit()

    def insert_or_replace_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT OR REPLACE INTO {UserRecord.table_name()} ({UserRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.username, self.fullname, self.password_hash, self.profiles, self.created_at, self.updated_at,
             self.commit_at)
        )
        conn.commit()

    def read_from_db_row(self, row: Dict[str, Any]):
        self.id = str(row["id"])
        self.username = row["username"]
        self.fullname = row["fullname"]
        self.password_hash = row["password_hash"]
        self.profiles = row.get("profiles", "")
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])

    def read_from_object(self, obj: User) -> None:
        self.id = str(obj.id)
        self.username = obj.username
        self.fullname = obj.fullname
        self.password_hash = obj.password_hash
        self.profiles = json.dumps([profile.dict() for profile in obj.profiles])
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at

    def convert_to_object(self) -> User:
        obj: User = User(
            id=uuid.UUID(self.id),
            username=self.username,
            fullname=self.fullname,
            password_hash=self.password_hash,
            profiles=ProfileRecord.from_json_to_list(self.profiles),
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at
        )
        return obj
