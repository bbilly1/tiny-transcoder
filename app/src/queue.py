"""interact with queue"""

from datetime import datetime
from pathlib import PosixPath

from src.base import Database
from src.static_types import QueueItem
from src.transcode import Transcoder
from src.utils import get_config, get_duration, get_file_size


class Queue:
    """represent the task queue"""

    VALID_STATE = ["pending", "transcoding", "completed", "pause"]
    CACHE_FOLDER: PosixPath = get_config()["cache_folder"]

    def add(self, path: PosixPath) -> list[QueueItem]:
        """add path to queue"""
        if not path.exists():
            raise FileNotFoundError(f"'{path.name}' does not exist")

        if path.is_dir():
            to_add = self._add_folder(path)
        elif path.is_file():
            to_add = self._add_file(path)
        else:
            raise ValueError(f"'{path.name}' not valid file or folder")

        return to_add

    def _add_folder(self, path: PosixPath) -> list[QueueItem]:
        """add folder to queue"""
        files = list(path.glob("*"))
        files.sort()
        to_add = [self._build_queue_item(i) for i in files]
        self._ingest(to_add)

        return to_add

    def _add_file(self, path: PosixPath) -> list[QueueItem]:
        """add single file"""
        to_add = [self._build_queue_item(path)]
        self._ingest(to_add)

        return to_add

    def _build_queue_item(self, path: PosixPath) -> QueueItem:
        """build dict to add"""
        queue_item: QueueItem = {
            "source_path": path,
            "source_name": path.name,
            "source_size": get_file_size(path),
            "duration": get_duration(path),
            "state": "pending",
            "date_added": datetime.now(),
        }

        return queue_item

    def _ingest(self, to_add: list[QueueItem]) -> None:
        """ingest list of items to queue"""
        columns = list(to_add[0].keys())
        query = (
            "INSERT INTO tasks "
            + f"({', '.join(columns)})"
            + " VALUES "
            + f"({', '.join([':' + col for col in columns])})"
        )
        db_handler = Database()
        for item in to_add:
            last_inserted_id = db_handler.execute(query, item)
            item["id"] = last_inserted_id

        db_handler.finish()

    def get_all(self, filter_by: None | str = None) -> list[QueueItem] | None:
        """get all items in queue"""
        if filter_by and filter_by not in self.VALID_STATE:
            raise ValueError("invalid filter")

        query = "SELECT * FROM tasks"
        if filter_by:
            query = f"{query} WHERE state = '{filter_by}'"

        query = (
            query
            + """
            ORDER BY
            CASE
                WHEN state = 'transcoding' THEN 1
                WHEN state = 'pending' THEN 2
                WHEN state = 'pause' THEN 3
                WHEN state = 'completed' THEN 4
                ELSE 5
            END;
            """
        )

        db_handler = Database()
        db_handler.execute(query)
        task_items: list[QueueItem] | None = db_handler.fetchall()
        db_handler.finish()

        return task_items

    def get_single(self, task_id: int) -> QueueItem:
        """get single queue item by id"""
        query = "SELECT * FROM tasks WHERE id = :id"
        value = {"id": int(task_id)}
        db_handler = Database()
        db_handler.execute(query, value)
        response = db_handler.fetchone()

        return response

    def get_next(self) -> QueueItem | None:
        """get next pending item in queue"""
        query = (
            "SELECT * FROM tasks WHERE state = 'pending' ORDER BY id LIMIT 1;"
        )
        db_handler = Database()
        db_handler.execute(query)
        next_item: QueueItem | None = db_handler.fetchone()
        db_handler.finish()

        return next_item

    def delete_single(self, task_id: int) -> None:
        """delete single item from queue"""
        query = "DELETE FROM tasks WHERE id = :id"
        value = {"id": int(task_id)}
        db_handler = Database()
        db_handler.execute(query, value)
        db_handler.finish()

    def clear(self, filter_by: None | str = None) -> None:
        """clear queue, optional filter_by"""
        if filter_by and filter_by not in self.VALID_STATE:
            raise ValueError("invalid filter")

        query = "DELETE FROM tasks"
        if filter_by:
            query = f"{query} WHERE state = '{filter_by}';"
        else:
            query = f"{query};"

        db_handler = Database()
        db_handler.execute(query)
        db_handler.finish()

    def is_running(self) -> bool:
        """check if queue is running"""
        return bool(set(self.CACHE_FOLDER.glob("*.mkv")))

    def run(self) -> None:
        """run queue until finished"""
        while True:
            next_item = self.get_next()
            if not next_item:
                print("queue is empty")
                break

            Transcoder(next_item).start()

    def run_single(self, item_id: int) -> None:
        """run transcode on single"""
        next_item = self.get_single(item_id)
        if not next_item:
            raise ValueError(f"task item not found: {item_id}")

        Transcoder(next_item).start()

    def update_state(self, item_id: int, state: str) -> None:
        """set state of item in queue"""
        if not state or state not in self.VALID_STATE:
            raise ValueError("invalid state")

        query = "UPDATE tasks SET state = :state WHERE id = :id;"
        value = {"id": int(item_id), "state": state}
        db_handler = Database()
        db_handler.execute(query, value)
        db_handler.finish()
