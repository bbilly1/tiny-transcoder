"""static typed dictionaries"""

from datetime import datetime
from pathlib import PosixPath
from typing import Literal, NotRequired, TypedDict


class QueueItem(TypedDict):
    """represent item in queue"""

    id: NotRequired[int]
    source_path: PosixPath
    source_name: str
    source_size: int
    dest_size: NotRequired[int]
    duration: int
    state: Literal["pending", "transcoding", "completed", "pause"]
    date_added: datetime
    date_started: NotRequired[datetime]
    date_completed: NotRequired[datetime]


class ProgressMessageType(TypedDict):
    """represent progress json data"""

    id: int
    name: str
    source_size: int
    fps: float
    duration: int
    transcode_size: int
    speed: float
    percent: float


class ConfigType(TypedDict):
    """represent config"""

    app_folder: PosixPath
    cache_folder: PosixPath
    ffmpeg_obs: dict
    hwaccel: str | None
