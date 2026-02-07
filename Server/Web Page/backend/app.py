from __future__ import annotations

import csv
import os
import time
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

import constants
from comm import ClientNotConnectedError, ConnectionManager


app = Flask(__name__, template_folder="../html", static_folder="../static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

DATA_CSV_PATH = Path(__file__).with_name("data.csv")

connection_manager = ConnectionManager(
    host=constants.HOST,
    control_port=constants.PORTOUT,
    video_port=constants.PORT_VIDEO,
    heartbeat_timeout_s=constants.HEARTBEAT_TIMEOUT_S,
    heartbeat_interval_s=constants.HEARTBEAT_INTERVAL_S,
    max_frame_bytes=constants.MAX_FRAME_BYTES,
    max_control_line_bytes=constants.MAX_CONTROL_LINE_BYTES,
)


def ensure_comm_ready() -> None:
    connection_manager.ensure_started()


@app.before_request
def bootstrap_comm() -> None:
    ensure_comm_ready()


def read_csv() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with DATA_CSV_PATH.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(dict(row))
    return data


def gen(client_id: str):
    while True:
        frame = connection_manager.get_latest_frame(client_id)
        if frame is not None:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(1 / constants.VIDEO_STREAM_FPS)


@app.route("/commandClient", methods=["POST"])
def command_client():
    ensure_comm_ready()

    raw = request.data.decode("utf-8").strip()
    if " on Client: " not in raw:
        return "Invalid command format. Use '<command> on Client: <id>'", 400

    command, client_id = raw.split(" on Client: ", 1)
    command = command.strip()
    client_id = client_id.strip()

    if not command:
        return "Command cannot be empty", 400
    if not client_id:
        return "Enter client id", 400

    try:
        event = connection_manager.send_command(client_id, command)
    except ClientNotConnectedError:
        return f"Client {client_id} is not connected.", 409
    except OSError as err:
        return f"Command send failed: {err}", 500

    return f"Command: '{command}' sent to client {client_id}. (msg_id={event.msg_id})"


@app.route("/video_feed/<client_id>")
def video_feed(client_id: str):
    ensure_comm_ready()
    if connection_manager.get_latest_frame(client_id) is None:
        return abort(404, description=f"No video stream for client {client_id}")
    return Response(
        gen(client_id), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/clients")
def clients():
    ensure_comm_ready()
    return jsonify(connection_manager.list_clients())


@app.route("/commandStatus/<msg_id>")
def command_status(msg_id: str):
    ensure_comm_ready()
    event = connection_manager.get_command_event(msg_id)
    if event is None:
        return abort(404, description=f"No command with msg_id={msg_id}")
    return jsonify(event)


@app.route("/commandHistory/<client_id>")
def command_history(client_id: str):
    ensure_comm_ready()
    limit = request.args.get("limit", default=100, type=int)
    events = connection_manager.list_command_events(client_id=client_id, limit=limit)
    return jsonify(events)


@app.route("/fetchData")
def get_data():
    return jsonify(read_csv())


@app.route("/404Error")
def open_error_page():
    return render_template("404.html")


@app.route("/dataDisplay")
def open_data_page():
    return render_template("DataDisplay.html")


@app.route("/motionControls")
def open_controls_page():
    return render_template("MotionControl.html")


@app.route("/exoDashboard")
def open_dashboard_page():
    return render_template("ExoDashboard.html")


@app.route("/exoDashboard/client/<client_id>")
def open_client_dashboard_page(client_id: str):
    return render_template("ExoClient.html", client_id=client_id)


@app.route("/")
def open_home_page():
    return render_template("Home.html")


@app.route("/health")
def health():
    ensure_comm_ready()
    return jsonify({"status": "ok", "comm_running": connection_manager.is_running()})


if __name__ == "__main__":
    ensure_comm_ready()
    print("RUNNING")
    host = os.getenv("EXO_HTTP_HOST", "127.0.0.1")
    port = int(os.getenv("EXO_HTTP_PORT", "5000"))
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)
