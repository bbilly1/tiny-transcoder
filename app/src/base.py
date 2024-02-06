"""database interaction"""

import sqlite3
from datetime import datetime
from pathlib import PosixPath

from src.utils import get_config


def adapt_datetime(datetime_obj: datetime) -> str:
    """convert to iso str"""
    return datetime_obj.isoformat()


def convert_datetime(datetime_bytes: bytes) -> datetime:
    """convert iso datetime to obj"""
    return datetime.fromisoformat(datetime_bytes.decode())


def adapt_path(path: PosixPath) -> str:
    """convert path to str"""
    return str(path.resolve())


def convert_path(path_bytes: bytes) -> PosixPath:
    """convert path string to obj"""
    return PosixPath(path_bytes.decode())


sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)
sqlite3.register_adapter(PosixPath, adapt_path)
sqlite3.register_converter("PosixPath", convert_path)


class Database:
    """handle all database actions"""

    DB_FILE: PosixPath = get_config()["app_folder"] / "queue.db"

    def __init__(self):
        self.conn = sqlite3.connect(
            self.DB_FILE,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        self.cursor = self.conn.cursor()

    def validate(self) -> bool:
        """make sure expected tables are there"""
        all_tables_query = """
            SELECT
                name
            FROM
                sqlite_schema
            WHERE
                type ='table' AND
                name NOT LIKE 'sqlite_%';
        """
        self.execute(all_tables_query)
        all_tables: list = self.fetchall()
        if not all_tables:
            print(f"[db] setup new database {self.DB_FILE}")
            self.setup()

        return not bool(all_tables)

    def setup(self) -> None:
        """setup empty database"""
        tasks_table: str = """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                source_path PosixPath UNIQUE,
                source_name VARCHAR(128),
                source_size integer,
                dest_size integer,
                duration integer,
                state VARCHAR(128),
                date_added DATETIME,
                date_started DATETIME,
                date_completed DATETIME
            )
        """
        message_table: str = """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY,
                message TEXT
            )
        """
        self.execute(tasks_table)
        self.execute(message_table)

    def execute(self, to_execute: str, values: dict | bool = False) -> int:
        """execute on the cursor"""
        if values:
            self.cursor.execute(to_execute, values)
        else:
            self.cursor.execute(to_execute)

        last_inserted_id = self.cursor.lastrowid

        return last_inserted_id

    def fetchall(self):
        """get all results"""
        stored_data = self.cursor.fetchall()
        if not stored_data:
            return []

        column_names = [desc[0] for desc in self.cursor.description]
        all_results = [dict(zip(column_names, i)) for i in stored_data]

        return all_results

    def fetchone(self):
        """get one result"""
        stored_data = self.cursor.fetchone()
        if not stored_data:
            return None

        column_names = [desc[0] for desc in self.cursor.description]
        result = dict(zip(column_names, stored_data))
        return result

    def finish(self) -> None:
        """close all"""
        self.conn.commit()
        self.conn.close()
