from __future__ import annotations

import io
import json
import socket
import struct
import threading
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

import constants

try:
    from picamera2 import Picamera2  # type: ignore[import-not-found]
except Exception:
    Picamera2 = None

try:
    import serial
except Exception:
    serial = None


class ClientAgent:
    def __init__(self):
        self.client_id = constants.CLIENT_ID
        self.sim_mode = constants.SIM_MODE
        try:
            self._overlay_font = ImageFont.load_default()
        except Exception:
            self._overlay_font = None

    def _log(self, message: str) -> None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{self.client_id}] {message}")

    def run_forever(self) -> None:
        self._log(f"Starting client agent sim_mode={self.sim_mode}")
        while True:
            try:
                self._run_session()
            except Exception as err:
                self._log(f"Agent session ended: {err}")
            time.sleep(constants.CONNECT_RETRY_S)

    def _run_session(self) -> None:
        control_sock = self._connect_with_retry(
            constants.HOST, constants.PORTIN, "control"
        )
        control_reader = control_sock.makefile("rb")

        hello = {
            "version": constants.PROTOCOL_VERSION,
            "type": "hello",
            "client_id": self.client_id,
            "session_id": None,
            "msg_id": uuid.uuid4().hex,
            "ts": time.time(),
            "payload": {
                "sim_mode": self.sim_mode,
            },
        }
        self._send_json_line(control_sock, hello)

        hello_ack = self._read_json_line(control_reader)
        if hello_ack is None or hello_ack.get("type") != "hello_ack":
            raise RuntimeError("Invalid hello_ack from server")

        session_id = str(hello_ack.get("session_id", "")).strip()
        if not session_id:
            raise RuntimeError("Server hello_ack missing session_id")

        self._log(f"Connected to server with session_id={session_id}")

        session_stop = threading.Event()
        video_thread = threading.Thread(
            target=self._video_loop,
            args=(session_id, session_stop),
            daemon=True,
        )
        heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            args=(control_sock, session_id, session_stop),
            daemon=True,
        )

        video_thread.start()
        heartbeat_thread.start()

        try:
            self._command_loop(control_sock, control_reader, session_id, session_stop)
        finally:
            session_stop.set()
            try:
                control_reader.close()
            except OSError:
                pass
            try:
                control_sock.close()
            except OSError:
                pass

    def _command_loop(
        self,
        control_sock: socket.socket,
        control_reader,
        session_id: str,
        session_stop: threading.Event,
    ) -> None:
        while not session_stop.is_set():
            msg = self._read_json_line(control_reader)
            if msg is None:
                raise RuntimeError("Server closed control connection")

            if msg.get("type") != "command":
                continue

            msg_id = str(msg.get("msg_id", "")).strip()
            command = str(msg.get("payload", {}).get("command", "")).strip()
            self._log(f"Received command msg_id={msg_id} command='{command}'")

            accepted = bool(command and msg_id)
            ack = {
                "version": constants.PROTOCOL_VERSION,
                "type": "command_ack",
                "client_id": self.client_id,
                "session_id": session_id,
                "msg_id": msg_id or uuid.uuid4().hex,
                "ts": time.time(),
                "payload": {
                    "accepted": accepted,
                },
            }
            self._send_json_line(control_sock, ack)
            self._log(f"Sent command_ack msg_id={ack['msg_id']} accepted={accepted}")

            if not accepted:
                continue

            status, detail = self._execute_command(command)
            result = {
                "version": constants.PROTOCOL_VERSION,
                "type": "command_result",
                "client_id": self.client_id,
                "session_id": session_id,
                "msg_id": msg_id,
                "ts": time.time(),
                "payload": {
                    "status": status,
                    "detail": detail,
                },
            }
            self._send_json_line(control_sock, result)
            self._log(
                f"Sent command_result msg_id={msg_id} status={status} detail='{detail}'"
            )

    def _execute_command(self, command: str) -> tuple[str, str]:
        try:
            if command.startswith("step "):
                parts = command.split(" ", 1)
                step_size = int(parts[1])
                self._turn_motor(step_size)
                return ("ok", f"step {step_size} executed")

            if command.startswith("display "):
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    return ("error", "display command must include index and message")
                index = int(parts[1])
                message = parts[2]
                self._display_text(index, message)
                return ("ok", f"display {index} executed")

            if command == "start_video":
                return ("ok", "video loop already active")

            return ("error", f"unsupported command: {command}")
        except Exception as err:
            return ("error", str(err))

    def _turn_motor(self, step_size: int) -> None:
        self._log(f"turnMotor step_size={step_size}")
        if self.sim_mode:
            self._log("SIM_MODE: skipping motor serial write")
            return
        if serial is None:
            raise RuntimeError("pyserial is not installed")

        with serial.Serial(constants.MOTOR_SERIALPORT, 9600) as ser:
            time.sleep(2)
            ser.write((f"step {step_size}\r").encode("utf-8"))

    def _display_text(self, index: int, message: str) -> None:
        self._log(f"display index={index} message={message}")
        if self.sim_mode:
            self._log("SIM_MODE: skipping OLED serial write")
            return
        if serial is None:
            raise RuntimeError("pyserial is not installed")

        with serial.Serial(constants.OLED_SERIALPORT, 9600) as ser:
            time.sleep(1)
            ser.write((f"display {index} {message}\r").encode("utf-8"))

    def _heartbeat_loop(
        self,
        control_sock: socket.socket,
        session_id: str,
        session_stop: threading.Event,
    ) -> None:
        while not session_stop.is_set():
            heartbeat = {
                "version": constants.PROTOCOL_VERSION,
                "type": "heartbeat",
                "client_id": self.client_id,
                "session_id": session_id,
                "msg_id": uuid.uuid4().hex,
                "ts": time.time(),
                "payload": {},
            }
            try:
                self._send_json_line(control_sock, heartbeat)
            except OSError:
                session_stop.set()
                return
            session_stop.wait(constants.HEARTBEAT_INTERVAL_S)

    def _video_loop(self, session_id: str, session_stop: threading.Event) -> None:
        video_sock = self._connect_with_retry(
            constants.HOST, constants.PORT_VIDEO, "video"
        )

        registration = {
            "version": constants.PROTOCOL_VERSION,
            "type": "video_hello",
            "client_id": self.client_id,
            "session_id": session_id,
            "msg_id": uuid.uuid4().hex,
            "ts": time.time(),
            "payload": {},
        }
        self._send_length_prefixed_json(video_sock, registration)

        use_camera = Picamera2 is not None and not self.sim_mode
        picam2 = None
        if use_camera and Picamera2 is not None:
            picam2 = Picamera2()
            config = picam2.create_still_configuration(
                main={"size": (640, 480)},
                buffer_count=1,
            )
            picam2.configure(config)
            picam2.start()
            time.sleep(2)
        else:
            use_camera = False
            self._log("SIM_MODE or no picamera2 detected: sending synthetic frames")

        frame_count = 0
        try:
            while not session_stop.is_set():
                if use_camera and picam2 is not None:
                    frame = self._frame_from_camera(picam2)
                else:
                    frame = self._frame_from_simulation(frame_count)

                video_sock.sendall(struct.pack(">I", len(frame)))
                video_sock.sendall(frame)

                frame_count += 1
                if frame_count % 30 == 0:
                    self._log(f"Sent {frame_count} frames")

                session_stop.wait(1 / constants.VIDEO_FPS)
        except OSError:
            session_stop.set()
        finally:
            if picam2 is not None:
                picam2.close()
            try:
                video_sock.close()
            except OSError:
                pass

    def _frame_from_camera(self, picam2) -> bytes:
        payload = io.BytesIO()
        array = picam2.capture_array()
        image = Image.fromarray(array)
        image.save(payload, format="JPEG", quality=70)
        return payload.getvalue()

    def _frame_from_simulation(self, frame_count: int) -> bytes:
        payload = io.BytesIO()
        color = (frame_count % 255, 100, 220)
        image = Image.new("RGB", (640, 480), color=color)

        overlay_text = f"Client: {self.client_id}\nTime: {time.strftime('%H:%M:%S')}"
        draw = ImageDraw.Draw(image)
        x, y, pad = 10, 10, 4

        try:
            if self._overlay_font is not None:
                bbox = draw.multiline_textbbox(
                    (x, y), overlay_text, font=self._overlay_font
                )
            else:
                bbox = draw.multiline_textbbox((x, y), overlay_text)
            bg_box = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
        except Exception:
            bg_box = (x - pad, y - pad, x + 210, y + 34)

        draw.rectangle(bg_box, fill=(0, 0, 0))
        if self._overlay_font is not None:
            draw.multiline_text(
                (x, y),
                overlay_text,
                fill=(255, 255, 255),
                font=self._overlay_font,
            )
        else:
            draw.multiline_text((x, y), overlay_text, fill=(255, 255, 255))

        image.save(payload, format="JPEG", quality=70)
        return payload.getvalue()

    def _connect_with_retry(self, host: str, port: int, label: str) -> socket.socket:
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._log(f"Connecting {label} socket to {host}:{port}")
                sock.connect((host, port))
                self._log(f"Connected {label} socket to {host}:{port}")
                return sock
            except OSError as err:
                sock.close()
                self._log(
                    f"{label} connect failed: {err}. Retrying in {constants.CONNECT_RETRY_S}s"
                )
                time.sleep(constants.CONNECT_RETRY_S)

    def _send_json_line(self, sock: socket.socket, payload: dict) -> None:
        encoded = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        sock.sendall(encoded)

    def _read_json_line(self, reader):
        line = reader.readline(constants.MAX_CONTROL_LINE_BYTES + 1)
        if not line:
            return None
        if len(line) > constants.MAX_CONTROL_LINE_BYTES:
            raise RuntimeError("Control line too large")
        return json.loads(line.decode("utf-8"))

    def _send_length_prefixed_json(self, sock: socket.socket, payload: dict) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        sock.sendall(struct.pack(">I", len(encoded)))
        sock.sendall(encoded)


if __name__ == "__main__":
    ClientAgent().run_forever()
