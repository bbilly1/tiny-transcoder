"""converter"""

import datetime
import shutil
import time
from pathlib import PosixPath

from ffmpeg import FFmpeg, Progress
from src.base import Database
from src.progress import ProgressMessage
from src.static_types import ConfigType, ProgressMessageType, QueueItem
from src.utils import get_config, get_file_size


class Transcoder:
    """implement transcode action on single item"""

    CONFIG: ConfigType = get_config()

    def __init__(self, queue_item: QueueItem):
        self.queue_item = queue_item
        self.last_progress_time = float(0)

    def start(self):
        """start process"""
        self.update_in_queue()
        cache_path = self.build_cache_path()
        self.transcode(cache_path)
        self.replace_original(cache_path)
        self.finish_in_queue()

    def update_in_queue(self):
        """set state in queue"""
        update_data = {
            "id": self.queue_item["id"],
            "state": "transcoding",
            "date_started": datetime.datetime.now(),
        }
        self._run_db_update(update_data)

    def build_cache_path(self):
        """build temporary path to transcode to"""
        return self.CONFIG["cache_folder"] / f"{self.queue_item['id']}.mkv"

    def transcode(self, cache_path):
        """invoke ffmpeg"""
        input_file = self.queue_item["source_path"]
        ffmpeg_obs = self.CONFIG["ffmpeg_obs"]

        input_kwargs = {}
        hwaccel = self.CONFIG["hwaccel"]
        if hwaccel:
            input_kwargs.update({"hwaccel": hwaccel})

        ffmpeg = (
            FFmpeg()
            .option("y")
            .input(input_file, **input_kwargs)
            .output(cache_path, ffmpeg_obs)
        )

        @ffmpeg.on("progress")
        def on_progress(progress: Progress):
            """on progress"""
            self.on_progress_callback(progress)

        ffmpeg.execute()

    def on_progress_callback(self, progress: Progress):
        """callback for ratelimiting"""
        current_time = time.time()
        elapsed_time = current_time - self.last_progress_time

        if elapsed_time <= 3:
            return

        duration = self.queue_item["duration"]
        progress_time = 0
        if duration:
            progress_time = progress.time.seconds / duration

        progress_message: ProgressMessageType = {
            "id": self.queue_item["id"],
            "name": self.queue_item["source_name"],
            "source_size": self.queue_item["source_size"],
            "duration": self.queue_item["duration"],
            "fps": progress.fps,
            "transcode_size": progress.size,
            "speed": progress.speed,
            "percent": round(progress_time, 4),
        }

        ProgressMessage().set_message(self.queue_item["id"], progress_message)
        self.last_progress_time = current_time

    def replace_original(self, cache_path: PosixPath):
        """replace original with transcoded file"""
        source = self.queue_item["source_path"]
        if cache_path.suffix != source.suffix:
            new_path = source.with_suffix(cache_path.suffix)
            source.rename(new_path)
            self.queue_item["source_path"] = new_path
            self.queue_item["source_name"] = new_path.name

        shutil.move(cache_path, self.queue_item["source_path"])

    def finish_in_queue(self):
        """set finish state in queue"""
        update_data = {
            "id": self.queue_item["id"],
            "state": "completed",
            "date_completed": datetime.datetime.now(),
            "dest_size": get_file_size(self.queue_item["source_path"]),
            "source_path": self.queue_item["source_path"],
            "source_name": self.queue_item["source_name"],
        }
        self._run_db_update(update_data)
        ProgressMessage().clear(self.queue_item["id"])

    def _run_db_update(self, update_data):
        """update item in queue"""
        update_query = (
            "UPDATE tasks SET "
            + f"{', '.join([f'{k} = :{k}' for k in update_data.keys()])} "
            + "WHERE id = :id"
        )
        db_handler = Database()
        db_handler.execute(update_query, update_data)
        db_handler.finish()
