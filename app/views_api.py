"""all api views"""

import json
from datetime import datetime
from multiprocessing import Process
from pathlib import PosixPath
from sqlite3 import IntegrityError

from flask import Blueprint, Response, request
from src.progress import ProgressMessage
from src.queue import Queue
from src.utils import clear_cache, kill_ffmpeg

api_blueprint = Blueprint("api", __name__)


class CustomEncoder(json.JSONEncoder):
    """handle custom object encoder"""

    def default(self, o):
        if isinstance(o, PosixPath):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def serialize_data(data):
    """custom serializer"""
    return json.dumps(data, cls=CustomEncoder)


def run_queue(item_id: int | None = None) -> None:
    """run the queue"""
    if item_id:
        Queue().run_single(item_id=item_id)
    else:
        Queue().run()


@api_blueprint.route("/queue", methods=["GET"])
def queue_list():
    """get list of items in queue"""
    filter_by = request.values.get("filter")
    all_items = Queue().get_all(filter_by)
    serialized_data = serialize_data(all_items)

    return Response(response=serialized_data, mimetype="application/json")


@api_blueprint.route("/queue", methods=["POST"])
def add_to_queue():
    """add path to queue"""
    data = request.get_json()
    path_data = data.get("path")
    if not path_data:
        return Response(response=data, status=400, mimetype="application/json")

    path = PosixPath(path_data)
    if not path.is_absolute():
        path = "/media" / path

    try:
        to_add = Queue().add(path)
    except (FileNotFoundError, ValueError, IntegrityError) as err:
        message = json.dumps({"message": err.args[0]})
        return Response(
            response=message, status=400, mimetype="application/json"
        )

    print(f"added: {to_add}")

    response = serialize_data(to_add)

    return Response(response=response, status=200, mimetype="application/json")


@api_blueprint.route("/queue", methods=["DELETE"])
def clear_queue():
    """delete queue"""
    filter_by = request.values.get("filter")
    message = json.dumps({"filter": filter_by, "action": "DELETE"})
    if not filter_by:
        kill_ffmpeg()
        clear_cache()
        ProgressMessage().clear_all()

    Queue().clear(filter_by)

    return Response(response=message, mimetype="application/json")


@api_blueprint.route("/queue/<int:task_id>", methods=["GET"])
def queue_item(task_id):
    """get single item"""
    single = Queue().get_single(task_id)
    if single:
        status = 200
        response = serialize_data(single)
    else:
        status = 404
        response = json.dumps({"message": "not found"})

    return Response(
        response=response, status=status, mimetype="application/json"
    )


@api_blueprint.route("/queue/<int:task_id>", methods=["POST"])
def queue_item_interact(task_id):
    """interact on single"""
    valid_actions = ["run", "pause", "pending"]
    single = Queue().get_single(task_id)
    if not single:
        response = json.dumps({"message": "not found"})
        return Response(
            response=response, status=404, mimetype="application/json"
        )

    data = request.get_json()
    action_data = data.get("action")
    if not action_data or action_data not in valid_actions:
        response = json.dumps({"message": "invalid action"})
        return Response(
            response=response, status=403, mimetype="application/json"
        )

    if action_data == "run":
        is_running = Queue().is_running()
        if is_running:
            response = json.dumps({"message": "queue locked"})
            return Response(
                response=response, status=400, mimetype="application/json"
            )

        process = Process(target=run_queue, daemon=True, args=(task_id,))
        process.start()
        ProgressMessage().wait()
        response = json.dumps({"message": f"task with ID {task_id}"})
        return Response(response=response, mimetype="application/json")

    if action_data in ["pending", "pause"]:
        Queue().update_state(task_id, action_data)
        response = json.dumps(
            {"message": f"update task {task_id} state to {action_data}"}
        )
        return Response(response=response, mimetype="application/json")

    return Response(status=403)


@api_blueprint.route("/queue/<int:task_id>", methods=["DELETE"])
def delete_queue_item(task_id):
    """delete item in queue"""
    task_item = Queue().get_single(task_id)
    if not task_item:
        response = json.dumps({"message": "not found"})
        return Response(
            response=response, status=404, mimetype="application/json"
        )

    Queue().delete_single(task_id)
    if task_item["state"] == "transcoding":
        kill_ffmpeg()
        clear_cache()
        ProgressMessage().clear(task_id)

    response = json.dumps({"message": "task deleted", "id": task_item["id"]})

    return Response(response=response, mimetype="application/json")


@api_blueprint.route("/progress")
def progress():
    """get progress"""
    response = ProgressMessage().get_message()

    return Response(response=response, mimetype="application/json")


@api_blueprint.route("/manage", methods=["POST"])
def run_queue_view():
    """trigger the queue"""
    is_running = Queue().is_running()
    if is_running:
        response = json.dumps({"message": "queue locked"})
        return Response(
            response=response, status=400, mimetype="application/json"
        )

    has_next = Queue().get_next()
    if has_next:
        process = Process(target=run_queue, daemon=True)
        process.start()
        ProgressMessage().wait()
        message = {"message": "queue started"}
    else:
        message = {"message": "queue is empty"}

    return Response(response=json.dumps(message), mimetype="application/json")


@api_blueprint.route("/manage", methods=["GET"])
def get_queue():
    """get queue status"""
    is_running = Queue().is_running()
    response = json.dumps({"task_in_progress": is_running})

    return Response(response=response, mimetype="application/json")
