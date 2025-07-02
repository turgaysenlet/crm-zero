import logging
import uuid
import time
from sqlite3 import Connection, Cursor
from typing import Optional

from pydantic import BaseModel, ConfigDict
import sqlite3
import json

from src.db.case_record import CaseRecord

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

    def init_db_schema(self) -> None:
        self.connect()

        # Create ObjectDefinition table
        cases_table = CaseRecord.table_definition()
        self.create_table(cases_table)

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
