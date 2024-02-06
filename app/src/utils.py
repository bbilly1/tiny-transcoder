"""collection of helper functions"""

import json
import subprocess
from math import ceil
from os import environ
from pathlib import PosixPath

import psutil
from src.static_types import ConfigType


def get_file_size(path: PosixPath) -> int:
    """get file size in MB"""
    if not path.exists():
        raise FileNotFoundError(f"The file '{path}' does not exist.")

    file_size_bytes = path.stat().st_size
    file_size_mb = round(file_size_bytes / (1024 * 1024))

    return file_size_mb


def get_duration(path: PosixPath) -> int:
    """get duration of media file from file path"""

    duration = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path.resolve()),
        ],
        capture_output=True,
        check=True,
    )
    duration_raw = duration.stdout.decode().strip()
    if duration_raw == "N/A":
        return 0

    duration_sec = ceil(float(duration_raw))

    return duration_sec


def get_config() -> ConfigType:
    """get config object"""
    config: ConfigType = {
        "app_folder": PosixPath(environ.get("TT_APP", "/data")),
        "cache_folder": PosixPath(environ.get("TT_CACHE", "/cache")),
        "ffmpeg_obs": json.loads(environ.get("TT_FFMPEG", "{}")),
        "hwaccel": environ.get("TT_HWACCEL", None),
    }

    return config


def kill_ffmpeg() -> None:
    """kill ffmpeg children"""
    for proc in psutil.process_iter(["pid", "name"]):
        if "ffmpeg" in proc.info["name"]:
            # Terminate the process
            proc.terminate()


def clear_cache() -> None:
    """delete all mkv files in cache folder"""
    cache_folder = get_config()["cache_folder"]
    for to_delete in cache_folder.glob("*.mkv"):
        to_delete.unlink()
