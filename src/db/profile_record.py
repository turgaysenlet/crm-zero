import json
import logging
import time
import uuid
from sqlite3 import Cursor, Connection
from typing import Dict, Any

from pydantic import BaseModel

from src.core.access.access_rule import AccessRule
from src.core.access.profile import Profile

logging.basicConfig()
logger = logging.getLogger("ProfileRecord")
logger.setLevel(logging.DEBUG)


class ProfileRecord(BaseModel):
    id: str
    name: str
    access_rules: str
    created_at: float = 0.0
    updated_at: float = 0.0
    commit_at: float = 0.0

    @classmethod
    def table_name(cls) -> str:
        return "Profiles"

    @classmethod
    def table_definition(cls) -> str:
        return f'''{ProfileRecord.table_name()} (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                access_rules TEXT,
                created_at FLOAT,
                updated_at FLOAT,
                commit_at FLOAT             
            )
        '''

    @classmethod
    def table_fields(cls) -> str:
        return f'id, name, access_rules, created_at, updated_at, commit_at'

    @classmethod
    def from_json_to_list(cls, profiles_json_str: str):
        j = json.loads(profiles_json_str or "[]")
        l = []
        for jj in j:
            l.append(
                Profile(
                    id=jj["id"],
                    name=jj["name"],
                    created_at=jj["created_at"],
                    updated_at=jj["updated_at"],
                    commit_at=jj["commit_at"],
                    access_rules=[AccessRule.from_json_dict(access_rule_dict) for
                                  access_rule_dict in json.loads(jj["access_rules"] or [])]
                )
            )
        return l

    @classmethod
    def from_object(cls, obj: Profile) -> "ProfileRecord":
        return ProfileRecord(
            id=str(obj.id),
            name=str(obj.name),
            access_rules=json.dumps([access_rule.to_json_dict() for access_rule in obj.access_rules]),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            commit_at=obj.commit_at
        )

    @classmethod
    def from_db_row(cls, row: Dict) -> "ProfileRecord":
        return ProfileRecord(
            id=row["id"],
            name=row["name"],
            access_rules=json.dumps([access_rule.to_json_dict() for access_rule in row.get("access_rules", [])]),
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
        logger.debug(f"Creating profile record: {self}")

    def insert_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT INTO {ProfileRecord.table_name()} ({ProfileRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.name, self.access_rules, self.created_at, self.updated_at, self.commit_at)
        )
        conn.commit()

    def insert_or_replace_to_db(self, conn: Connection, cursor: Cursor):
        now = time.time()
        self.commit_at = now
        query = f"INSERT OR REPLACE INTO {ProfileRecord.table_name()} ({ProfileRecord.table_fields()}) " \
                f"VALUES (?, ?, ?, ?, ?, ?)"
        logger.debug(f'Running SQL query "{query}"')
        cursor.execute(
            query,
            (self.id, self.name, self.access_rules, self.created_at, self.updated_at, self.commit_at)
        )
        conn.commit()

    def read_from_db_row(self, row: Dict[str, Any]):
        self.id = str(row["id"])
        self.name = row["name"]
        self.access_rules = json.dumps([access_rule.to_json_dict() for access_rule in row.get("access_rules", [])])
        self.created_at = float(row["created_at"])
        self.updated_at = float(row["updated_at"])
        self.commit_at = float(row["commit_at"])

    def read_from_object(self, obj: Profile) -> None:
        self.id = str(obj.id)
        self.name = obj.name
        self.access_rules = json.dumps([access_rule.to_json_dict() for access_rule in obj.access_rules])
        self.created_at = obj.created_at
        self.updated_at = obj.updated_at
        self.commit_at = obj.commit_at

    def convert_to_object(self) -> Profile:
        obj: Profile = Profile(
            id=uuid.UUID(self.id),
            name=self.name,
            access_rules=json.loads(self.access_rules or "[]"),
            created_at=self.created_at,
            updated_at=self.updated_at,
            commit_at=self.commit_at
        )
        return obj
