import logging
import uuid
import time
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Optional, Type, List

from pydantic import BaseModel, ConfigDict
import sqlite3
import json

from src.core.access.access_rule import AccessRule
from src.core.access.user import User
from src.core.base.data_object import DataObject
from src.db.case_record import CaseRecord
from src.db.profile_record import ProfileRecord
from src.db.user_record import UserRecord

logging.basicConfig()
logger = logging.getLogger("Database")
logger.setLevel(logging.DEBUG)


class Database(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Apply this here

    db_name: str
    conn: Optional[Connection] = None  # Connection object
    cursor: Optional[Cursor] = None  # Cursor object

    def __init__(self, **data):
        super().__init__(**data)
        logger.info(f"Initializing database at {self.db_name}")
        self.connect()
        self.init_db_schema()

    def connect(self) -> Connection:
        try:
            self.conn = None
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row  # Allows accessing columns by name
            self.cursor = self.conn.cursor()
            logger.debug(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
        return self.conn

    def delete_if_exists(self) -> None:
        file_path = Path(self.db_name)
        if file_path.exists():
            logger.debug(f'Deleting database: "{self.db_name}"')
            file_path.unlink()
        else:
            logger.debug(f'No database to delete: "{self.db_name}"')

    def init_db_schema(self) -> None:
        self.connect()

        # Create tables
        self.create_table(CaseRecord.table_definition())
        self.create_table(UserRecord.table_definition())
        self.create_table(ProfileRecord.table_definition())

        self.conn.commit()
        self.conn.close()

    def create_table(self, cases_table):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {cases_table}
        ''')

    def list_table_rows(self, table_name: str, where: Optional[str] = None) -> [dict]:
        """
        Lists all records from the specified table.
        Returns a list of dictionaries, where each dictionary represents a row.
        """
        if not self.conn:
            logger.error("Database connection not established. Cannot list table.")
            return []

        try:
            query = f"SELECT * FROM {table_name}"
            if where is not None:
                query = f"{query} WHERE {where}"
            logger.debug(f'Running SQL query "{query}"')
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logger.debug(f'Received rows: "{rows}"')
            # Convert sqlite3.Row objects to dictionaries for easier handling
            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            logger.error(f"Error: Table '{table_name}' does not exist or SQL error. {e}")
            return []
        except sqlite3.Error as e:
            logger.error(f"Error listing table '{table_name}': {e}")
            return []

    def read_max_case_number(self) -> int:
        max_case_number: int = 0
        if not self.conn:
            logger.error("Database connection not established. Cannot list table.")
            return max_case_number

        try:
            query = CaseRecord.get_last_case_number_query()
            logger.debug(f'Running SQL query "{query}"')
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logger.debug(f'Received rows: "{rows}"')
            if len(rows) > 0:
                row = dict(rows[0])
                max_case_number_value = row.get("max_case_number", max_case_number)
                if max_case_number_value is None:
                    max_case_number_value = max_case_number
                logger.info(f"Last case number in database is {max_case_number_value}.")
                return max_case_number_value
            return max_case_number
        except sqlite3.OperationalError as e:
            logger.error(f"Error: Table '{CaseRecord.table_name()}' does not exist or SQL error. {e}")
            return max_case_number
        except sqlite3.Error as e:
            logger.error(f"Error listing table '{CaseRecord.table_name()}': {e}")
            return max_case_number

    def read_objects(self, table_name: str, object_type_str: str, user: Optional[User]) -> [DataObject]:
        """
        Read all records from the specified table, by applying user based access rules.
        Returns object of the given type.
        """
        if not self.conn:
            logger.error("Database connection not established. Cannot list table.")
            return []

        access_rules: List[AccessRule] = []
        if user is not None:
            for profile in user.profiles:
                access_rules.extend(profile.access_rules)
            data_object_types: List[str] = [access_rule.data_object_type for access_rule in access_rules]
            if data_object_types.__contains__(object_type_str):
                rows = self.list_table_rows(table_name)
                if object_type_str == "Case":
                    return [CaseRecord.from_db_row(row) for row in rows]
                logger.warning(
                    f'Unexpected object type "{object_type_str}".')
                return []
            else:
                logger.warning(f'User "{user.username}" trying to access object type "{object_type_str}", '
                               f'but does not have access.')
                return []
        else:
            if object_type_str == "User":
                rows = self.list_table_rows(table_name)
                return [UserRecord.from_db_row(row) for row in rows]
            else:
                logger.warning(
                    f'Unexpected object type "{object_type_str}".')
                return []
