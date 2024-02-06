"""handle transcode progress"""

import json
from time import sleep

from src.base import Database
from src.static_types import ProgressMessageType


class ProgressMessage:
    """interact with progress"""

    def set_message(
        self, item_id: int, progress_message: ProgressMessageType
    ) -> None:
        """write progress to db"""
        to_write = {"id": item_id, "message": json.dumps(progress_message)}
        columns = list(to_write.keys())
        query = (
            "INSERT OR REPLACE INTO progress "
            + f"({', '.join(columns)})"
            + " VALUES "
            + f"({', '.join([':' + col for col in columns])})"
        )
        db_handler = Database()
        db_handler.execute(query, values=to_write)
        db_handler.finish()

    def get_message(self) -> str | None:
        """get progress message"""
        query = "SELECT message FROM progress;"
        db_handler = Database()
        db_handler.execute(query)
        progress_message = db_handler.fetchone()
        db_handler.finish()

        if progress_message:
            progress_message = progress_message.get("message")

        return progress_message

    def clear(self, item_id: int) -> None:
        """clear progress message"""
        clear = "DELETE FROM progress WHERE id = :id"
        value = {"id": int(item_id)}

        db_handler = Database()
        db_handler.execute(clear, value)
        db_handler.finish()

    def clear_all(self) -> None:
        """clear all progress messages"""
        clear = "DELETE FROM progress;"
        db_handler = Database()
        db_handler.execute(clear)
        db_handler.finish()

    def wait(self) -> None:
        """wait for progress message to appear"""
        query = "SELECT EXISTS (SELECT 1 FROM progress);"
        db_handler = Database()
        for _ in range(20):
            db_handler.execute(query)
            response = db_handler.fetchone()
            if response and list(response.values())[0]:
                break

            sleep(0.25)

        db_handler.finish()
