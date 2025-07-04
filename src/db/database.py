import logging
import sqlite3
import uuid
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict

from src.core.access.access_rule import AccessRule
from src.core.access.profile import Profile
from src.core.access.user import User
from src.core.base.data_object import DataObject
from src.db.account_record import AccountRecord
from src.db.case_record import CaseRecord
from src.db.profile_record import ProfileRecord
from src.db.user_record import UserRecord
from src.db.workflow_record import WorkflowRecord
from src.db.workflow_step_record import WorkflowStepRecord

logging.basicConfig()
logger = logging.getLogger("Database")
logger.setLevel(logging.DEBUG)


class Database(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # Apply this here

    db_name: str

    def __init__(self, **data):
        super().__init__(**data)
        logger.info(f"Initializing database at {self.db_name}")
        [conn, cursor] = self.connect()
        self.init_db_schema(conn, cursor)
        conn.close()

    def connect(self) -> [Connection, Cursor]:
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row  # Allows accessing columns by name
            cursor = conn.cursor()
            logger.debug(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
        return [conn, cursor]

    def delete_if_exists(self) -> None:
        file_path = Path(self.db_name)
        if file_path.exists():
            logger.debug(f'Deleting database: "{self.db_name}"')
            file_path.unlink()
        else:
            logger.debug(f'No database to delete: "{self.db_name}"')

    def init_db_schema(self, conn: Connection, cursor: Cursor) -> None:
        # Create tables
        self.create_table(conn, cursor, AccountRecord.table_definition())
        self.create_table(conn, cursor, CaseRecord.table_definition())
        self.create_table(conn, cursor, UserRecord.table_definition())
        self.create_table(conn, cursor, ProfileRecord.table_definition())
        self.create_table(conn, cursor, WorkflowRecord.table_definition())
        self.create_table(conn, cursor, WorkflowStepRecord.table_definition())

        conn.commit()
        conn.close()

    def create_table(self, conn: Connection, cursor: Cursor, table_name):
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name}
        ''')

    def get_table_row(self, conn: Connection, cursor: Cursor, table_name: str, id: uuid.UUID) -> [dict]:
        """
        Reads one record from the specified table, based on the id field.
        Returns a list of dictionaries, where each dictionary represents a row.
        """
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return []

        try:
            query = f"SELECT * FROM {table_name} WHERE id='{str(id)}'"
            logger.debug(f'Running SQL query "{query}"')
            cursor.execute(query)
            rows = cursor.fetchall()
            logger.debug(f'Received rows: "{rows}"')
            # Convert sqlite3.Row objects to dictionaries for easier handling
            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            logger.error(f"Error: Table '{table_name}' does not exist or SQL error. {e}")
            return []
        except sqlite3.Error as e:
            logger.error(f"Error listing table '{table_name}': {e}")
            return []

    def list_table_rows(self, conn: Connection, cursor: Cursor, table_name: str, where: Optional[str] = None) -> [dict]:
        """
        Lists all records from the specified table.
        Returns a list of dictionaries, where each dictionary represents a row.
        """
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return []

        try:
            query = f"SELECT * FROM {table_name}"
            if where is not None:
                query = f"{query} WHERE {where}"
            logger.debug(f'Running SQL query "{query}"')
            cursor.execute(query)
            rows = cursor.fetchall()
            logger.debug(f'Received rows: "{rows}"')
            # Convert sqlite3.Row objects to dictionaries for easier handling
            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            logger.error(f"Error: Table '{table_name}' does not exist or SQL error. {e}")
            return []
        except sqlite3.Error as e:
            logger.error(f"Error listing table '{table_name}': {e}")
            return []

    def read_max_case_number(self, conn: Connection, cursor: Cursor) -> int:
        max_case_number: int = 0
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return max_case_number

        try:
            query = CaseRecord.get_last_case_number_query()
            logger.debug(f'Running SQL query "{query}"')
            cursor.execute(query)
            rows = cursor.fetchall()
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

    def read_max_account_number(self, conn: Connection, cursor: Cursor) -> int:
        max_account_number: int = 0
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return max_account_number

        try:
            query = AccountRecord.get_last_account_number_query()
            logger.debug(f'Running SQL query "{query}"')
            cursor.execute(query)
            rows = cursor.fetchall()
            logger.debug(f'Received rows: "{rows}"')
            if len(rows) > 0:
                row = dict(rows[0])
                max_account_number_value = row.get("max_account_number", max_account_number)
                if max_account_number_value is None:
                    max_account_number_value = max_account_number
                logger.info(f"Last account number in database is {max_account_number_value}.")
                return max_account_number_value
            return max_account_number
        except sqlite3.OperationalError as e:
            logger.error(f"Error: Table '{AccountRecord.table_name()}' does not exist or SQL error. {e}")
            return max_account_number
        except sqlite3.Error as e:
            logger.error(f"Error listing table '{AccountRecord.table_name()}': {e}")
            return max_account_number

    def read_objects(self, conn: Connection, cursor: Cursor, table_name: str, object_type_str: str, user: Optional[User]) -> [DataObject]:
        """
        Read all records from the specified table, by applying user based access rules.
        Returns object of the given type.
        """
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return []

        # Check access
        allow_access = self.check_access(conn, cursor, object_type_str, user)
        # Read from DB
        if allow_access:
            rows = self.list_table_rows(conn, cursor, table_name)
            if rows is not None and len(rows) > 0:
                if object_type_str == "Case":
                    return [CaseRecord.from_db_row(row) for row in rows]
                elif object_type_str == "Account":
                    return [AccountRecord.from_db_row(row) for row in rows]
                elif object_type_str == "User":
                    return [UserRecord.from_db_row(row) for row in rows]
                elif object_type_str == "Profile":
                    return [ProfileRecord.from_db_row(row) for row in rows]
                elif object_type_str == "Workflow":
                    return [WorkflowRecord.from_db_row(row) for row in rows]
                elif object_type_str == "WorkflowStep":
                    return [WorkflowStepRecord.from_db_row(row) for row in rows]
                else:
                    # Unexpected object type
                    logger.warning(f'Unexpected object type "{object_type_str}".')
                return []
        else:
            logger.warning(f'User "{user.username}" trying to access object type "{object_type_str}", '
                           f'but does not have access.')
            return []

    def read_object_by_id(self, conn: Connection, cursor: Cursor, table_name: str, object_type_str: str,
                          object_id: uuid.UUID, user: Optional[User]) -> Any:
        """
        Read all records from the specified table, by applying user based access rules.
        Returns object of the given type.
        """
        if not conn:
            logger.error("Database connection not established. Cannot list table.")
            return []
        # Check access
        allow_access = self.check_access(conn, cursor, object_type_str, user)
        # Read from DB
        if allow_access:
            rows = self.get_table_row(conn, cursor, table_name, object_id)
            if rows is not None and len(rows) > 0:
                row = rows[0]
                if object_type_str == "Case":
                    return CaseRecord.from_db_row(row)
                elif object_type_str == "Account":
                    return AccountRecord.from_db_row(row)
                elif object_type_str == "User":
                    return UserRecord.from_db_row(row)
                elif object_type_str == "Profile":
                    return ProfileRecord.from_db_row(row)
                elif object_type_str == "Workflow":
                    return WorkflowRecord.from_db_row(row)
                elif object_type_str == "WorkflowStep":
                    return WorkflowStepRecord.from_db_row(row)
                else:
                    # Unexpected object type
                    logger.warning(f'Unexpected object type "{object_type_str}".')
                return None
            else:
                # No rows
                logger.warning(f'No object of id "{object_id}" and type "{object_type_str}" found.')
                return None
        else:
            # No access
            logger.warning(f'User "{user.username}" trying to access object type "{object_type_str}", '
                           f'but does not have access.')
            return None

    def get_profiles(self, conn: Connection, cursor: Cursor) -> List[Profile]:
        # TODO: Potential infinite stack due to read_objects calling check_access and check_access calling read_objects.
        profile_records: List[ProfileRecord] = self.read_objects(conn, cursor, ProfileRecord.table_name(), "Profile", None)
        profiles: List[Profile] = [profile_record.convert_to_object() for profile_record in profile_records]
        if not profiles:
            return []
        return profiles

    def check_access(self, conn: Connection, cursor: Cursor, object_type_str: str, user: User):
        allow_access = AccessRule.object_type_accessible_to_all(object_type_str)
        access_rules: List[AccessRule] = []
        if user is not None:
            all_profiles = self.get_profiles(conn, cursor)
            all_profiles_dict = {profile.id: profile for profile in all_profiles}
            for profile_id in user.profile_ids.object_ids:
                found_profile = all_profiles_dict[profile_id]
                access_rules.extend(found_profile.access_rules)
            data_object_types: List[str] = [access_rule.data_object_type for access_rule in access_rules]
            if data_object_types.__contains__(object_type_str):
                allow_access = True
        return allow_access
