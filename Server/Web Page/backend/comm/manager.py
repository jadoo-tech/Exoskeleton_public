from __future__ import annotations

import json
import socket
import struct
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, BinaryIO


class ClientNotConnectedError(Exception):
    pass


class ProtocolError(Exception):
    pass


@dataclass
class CommandEvent:
    msg_id: str
    client_id: str
    command: str
    sent_at: float
    ack: dict[str, Any] | None = None
    acked_at: float | None = None
    result: dict[str, Any] | None = None
    result_at: float | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "client_id": self.client_id,
            "command": self.command,
            "sent_at": self.sent_at,
            "ack": self.ack,
            "acked_at": self.acked_at,
            "result": self.result,
            "result_at": self.result_at,
        }


@dataclass
class ClientSession:
    client_id: str
    session_id: str
    control_conn: socket.socket
    control_reader: BinaryIO
    control_addr: tuple[str, int]
    connected_at: float
    last_heartbeat: float
    control_send_lock: threading.Lock = field(default_factory=threading.Lock)
    video_conn: socket.socket | None = None
    video_addr: tuple[str, int] | None = None


class ConnectionManager:
    def __init__(
        self,
        host: str,
        control_port: int,
        video_port: int,
        heartbeat_timeout_s: float,
        heartbeat_interval_s: float,
        max_frame_bytes: int,
        max_control_line_bytes: int,
    ):
        self.host = host
        self.control_port = control_port
        self.video_port = video_port
        self.heartbeat_timeout_s = heartbeat_timeout_s
        self.heartbeat_interval_s = heartbeat_interval_s
        self.max_frame_bytes = max_frame_bytes
        self.max_control_line_bytes = max_control_line_bytes

        self._running = False
        self._state_lock = threading.RLock()
        self._stop_event = threading.Event()

        self._control_listener: socket.socket | None = None
        self._video_listener: socket.socket | None = None

        self._sessions: dict[str, ClientSession] = {}
        self._latest_frames: dict[str, bytes] = {}
        self._command_events: dict[str, CommandEvent] = {}

    def ensure_started(self) -> None:
        with self._state_lock:
            if self._running:
                return
            self._stop_event.clear()
            self._control_listener = self._create_listener(self.host, self.control_port)
            self._video_listener = self._create_listener(self.host, self.video_port)
            self._running = True

        threading.Thread(target=self._accept_control_loop, daemon=True).start()
        threading.Thread(target=self._accept_video_loop, daemon=True).start()
        threading.Thread(target=self._heartbeat_monitor_loop, daemon=True).start()
        print(
            f"ConnectionManager listening on control={self.control_port}, video={self.video_port}"
        )

    def stop(self) -> None:
        with self._state_lock:
            self._running = False
            self._stop_event.set()
            control_listener = self._control_listener
            video_listener = self._video_listener
            self._control_listener = None
            self._video_listener = None
            sessions = list(self._sessions.values())
            self._sessions.clear()
            self._latest_frames.clear()

        self._close_socket(control_listener)
        self._close_socket(video_listener)

        for session in sessions:
            self._close_session_sockets(session)

    def reset_for_tests(self) -> None:
        with self._state_lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
            self._latest_frames.clear()
            self._command_events.clear()
        for session in sessions:
            self._close_session_sockets(session)

    def is_running(self) -> bool:
        with self._state_lock:
            return self._running

    def get_latest_frame(self, client_id: str) -> bytes | None:
        with self._state_lock:
            return self._latest_frames.get(client_id)

    def list_clients(self) -> list[dict[str, Any]]:
        with self._state_lock:
            clients = []
            for client_id, session in self._sessions.items():
                clients.append(
                    {
                        "client_id": client_id,
                        "session_id": session.session_id,
                        "connected_at": session.connected_at,
                        "last_heartbeat": session.last_heartbeat,
                        "video_connected": session.video_conn is not None,
                    }
                )
            return clients

    def send_command(self, client_id: str, command: str) -> CommandEvent:
        with self._state_lock:
            session = self._sessions.get(client_id)
            if session is None:
                raise ClientNotConnectedError(f"Client {client_id} is not connected")

        msg_id = uuid.uuid4().hex
        event = CommandEvent(
            msg_id=msg_id,
            client_id=client_id,
            command=command,
            sent_at=time.time(),
        )

        message = {
            "version": 1,
            "type": "command",
            "client_id": client_id,
            "session_id": session.session_id,
            "msg_id": msg_id,
            "ts": time.time(),
            "payload": {"command": command},
        }

        try:
            self._send_json(session.control_conn, session.control_send_lock, message)
        except OSError as err:
            self._drop_session(client_id, session.session_id)
            raise ClientNotConnectedError(
                f"Client {client_id} disconnected while sending command"
            ) from err

        with self._state_lock:
            self._command_events[msg_id] = event

        return event

    def get_command_event(self, msg_id: str) -> dict[str, Any] | None:
        with self._state_lock:
            event = self._command_events.get(msg_id)
            if event is None:
                return None
            return event.snapshot()

    def list_command_events(
        self,
        client_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 500))
        with self._state_lock:
            events = []
            for event in self._command_events.values():
                if client_id is not None and event.client_id != client_id:
                    continue
                events.append(event.snapshot())

        events.sort(key=lambda item: item["sent_at"], reverse=True)
        return events[:safe_limit]

    def _accept_control_loop(self) -> None:
        while not self._stop_event.is_set():
            listener = self._control_listener
            if listener is None:
                return

            try:
                conn, addr = listener.accept()
            except OSError:
                if self._stop_event.is_set():
                    return
                continue

            threading.Thread(
                target=self._initialize_control_connection,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _initialize_control_connection(
        self, conn: socket.socket, addr: tuple[str, int]
    ) -> None:
        try:
            conn.settimeout(15)
            reader = conn.makefile("rb")
            hello = self._read_json_line(reader)
            if hello is None:
                raise ProtocolError("Empty hello message")

            if hello.get("type") != "hello":
                raise ProtocolError("First control message must be type=hello")

            client_id = str(hello.get("client_id", "")).strip()
            if not client_id:
                raise ProtocolError("hello message missing client_id")

            session_id = uuid.uuid4().hex
            now = time.time()
            session = ClientSession(
                client_id=client_id,
                session_id=session_id,
                control_conn=conn,
                control_reader=reader,
                control_addr=addr,
                connected_at=now,
                last_heartbeat=now,
            )

            with self._state_lock:
                existing = self._sessions.get(client_id)
                self._sessions[client_id] = session

            if existing is not None:
                self._close_session_sockets(existing)

            ack = {
                "version": 1,
                "type": "hello_ack",
                "client_id": client_id,
                "session_id": session_id,
                "msg_id": uuid.uuid4().hex,
                "ts": time.time(),
                "payload": {
                    "heartbeat_interval_s": self.heartbeat_interval_s,
                },
            }

            conn.settimeout(None)
            self._send_json(conn, session.control_send_lock, ack)
            print(f"Control client connected: {client_id} session={session_id}")

            self._control_reader_loop(session)
        except Exception as err:
            print(f"Control connection init failed: {err}")
            self._close_socket(conn)

    def _control_reader_loop(self, session: ClientSession) -> None:
        try:
            while not self._stop_event.is_set():
                msg = self._read_json_line(session.control_reader)
                if msg is None:
                    break

                msg_type = msg.get("type")
                if msg_type == "heartbeat":
                    with self._state_lock:
                        current = self._sessions.get(session.client_id)
                        if current and current.session_id == session.session_id:
                            current.last_heartbeat = time.time()
                    continue

                msg_id = str(msg.get("msg_id", ""))
                if not msg_id:
                    continue

                with self._state_lock:
                    event = self._command_events.get(msg_id)
                    if event is None:
                        continue

                    if msg_type == "command_ack":
                        event.ack = msg.get("payload")
                        event.acked_at = time.time()
                    elif msg_type == "command_result":
                        event.result = msg.get("payload")
                        event.result_at = time.time()
        except Exception as err:
            print(f"Control reader loop ended for {session.client_id}: {err}")
        finally:
            self._drop_session(session.client_id, session.session_id)

    def _accept_video_loop(self) -> None:
        while not self._stop_event.is_set():
            listener = self._video_listener
            if listener is None:
                return

            try:
                conn, addr = listener.accept()
            except OSError:
                if self._stop_event.is_set():
                    return
                continue

            threading.Thread(
                target=self._initialize_video_connection,
                args=(conn, addr),
                daemon=True,
            ).start()

    def _initialize_video_connection(
        self, conn: socket.socket, addr: tuple[str, int]
    ) -> None:
        client_id = ""
        session_id = ""
        try:
            conn.settimeout(15)
            registration = self._recv_length_prefixed_json(conn)

            if registration.get("type") != "video_hello":
                raise ProtocolError("First video message must be type=video_hello")

            client_id = str(registration.get("client_id", "")).strip()
            session_id = str(registration.get("session_id", "")).strip()
            if not client_id or not session_id:
                raise ProtocolError("video_hello missing client_id/session_id")

            with self._state_lock:
                session = self._sessions.get(client_id)
                if session is None or session.session_id != session_id:
                    raise ClientNotConnectedError(
                        f"Video session mismatch for client {client_id}"
                    )
                old_video_conn = session.video_conn
                session.video_conn = conn
                session.video_addr = addr

            self._close_socket(old_video_conn)
            conn.settimeout(None)
            print(f"Video client connected: {client_id} session={session_id}")
            self._video_reader_loop(client_id, session_id, conn)
        except Exception as err:
            print(f"Video connection init failed: {err}")
            self._close_socket(conn)
            if client_id and session_id:
                with self._state_lock:
                    session = self._sessions.get(client_id)
                    if (
                        session
                        and session.session_id == session_id
                        and session.video_conn is conn
                    ):
                        session.video_conn = None
                        session.video_addr = None

    def _video_reader_loop(
        self,
        client_id: str,
        session_id: str,
        conn: socket.socket,
    ) -> None:
        try:
            while not self._stop_event.is_set():
                header = self._recv_exact(conn, 4)
                if header is None:
                    break

                frame_size = struct.unpack(">I", header)[0]
                if frame_size <= 0 or frame_size > self.max_frame_bytes:
                    raise ProtocolError(
                        f"Invalid frame size {frame_size} for client {client_id}"
                    )

                frame = self._recv_exact(conn, frame_size)
                if frame is None:
                    break

                with self._state_lock:
                    session = self._sessions.get(client_id)
                    if session is None or session.session_id != session_id:
                        break
                    self._latest_frames[client_id] = frame
        except Exception as err:
            print(f"Video reader loop ended for {client_id}: {err}")
        finally:
            self._close_socket(conn)
            with self._state_lock:
                session = self._sessions.get(client_id)
                if (
                    session
                    and session.session_id == session_id
                    and session.video_conn is conn
                ):
                    session.video_conn = None
                    session.video_addr = None

    def _heartbeat_monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            stale: list[tuple[str, str]] = []
            now = time.time()
            with self._state_lock:
                for client_id, session in self._sessions.items():
                    if now - session.last_heartbeat > self.heartbeat_timeout_s:
                        stale.append((client_id, session.session_id))

            for client_id, session_id in stale:
                print(f"Heartbeat timeout for {client_id}, dropping session")
                self._drop_session(client_id, session_id)

            self._stop_event.wait(1.0)

    def _drop_session(self, client_id: str, session_id: str) -> None:
        with self._state_lock:
            session = self._sessions.get(client_id)
            if session is None or session.session_id != session_id:
                return
            self._sessions.pop(client_id, None)
            self._latest_frames.pop(client_id, None)

        self._close_session_sockets(session)

    def _close_session_sockets(self, session: ClientSession) -> None:
        self._close_socket(session.video_conn)
        self._close_socket(session.control_reader)
        self._close_socket(session.control_conn)

    def _create_listener(self, host: str, port: int) -> socket.socket:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(32)
        return listener

    def _send_json(
        self,
        conn: socket.socket,
        send_lock: threading.Lock,
        message: dict[str, Any],
    ) -> None:
        encoded = (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")
        with send_lock:
            conn.sendall(encoded)

    def _read_json_line(self, reader: BinaryIO) -> dict[str, Any] | None:
        line = reader.readline(self.max_control_line_bytes + 1)
        if not line:
            return None
        if len(line) > self.max_control_line_bytes:
            raise ProtocolError("Control message exceeded max line length")

        text = line.decode("utf-8").strip()
        if not text:
            return None

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as err:
            raise ProtocolError(f"Invalid JSON control line: {err}") from err

        if not isinstance(parsed, dict):
            raise ProtocolError("Control JSON payload must be an object")
        return parsed

    def _recv_length_prefixed_json(self, conn: socket.socket) -> dict[str, Any]:
        header = self._recv_exact(conn, 4)
        if header is None:
            raise ProtocolError("Missing length-prefixed registration header")

        payload_size = struct.unpack(">I", header)[0]
        if payload_size <= 0 or payload_size > self.max_control_line_bytes:
            raise ProtocolError(f"Invalid registration payload size {payload_size}")

        payload = self._recv_exact(conn, payload_size)
        if payload is None:
            raise ProtocolError("Incomplete registration payload")

        try:
            parsed = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as err:
            raise ProtocolError(f"Invalid registration JSON: {err}") from err

        if not isinstance(parsed, dict):
            raise ProtocolError("Registration JSON payload must be an object")
        return parsed

    def _recv_exact(self, conn: socket.socket, count: int) -> bytes | None:
        data = bytearray()
        while len(data) < count:
            chunk = conn.recv(count - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def _close_socket(self, resource: Any) -> None:
        if resource is None:
            return
        try:
            resource.close()
        except OSError:
            pass
