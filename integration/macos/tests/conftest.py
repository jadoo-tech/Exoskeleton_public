from __future__ import annotations

import importlib
import os
import socket
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "Server" / "Web Page" / "backend"


def _free_tcp_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture(scope="session")
def backend_module():
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))

    constants = importlib.import_module("constants")
    setattr(constants, "HOST", "127.0.0.1")
    setattr(constants, "PORTOUT", _free_tcp_port())
    setattr(constants, "PORT_VIDEO", _free_tcp_port())

    original_cwd = os.getcwd()
    os.chdir(BACKEND_DIR)

    app_module = importlib.import_module("app")
    yield app_module

    app_module.connection_manager.stop()
    os.chdir(original_cwd)


@pytest.fixture(autouse=True)
def reset_backend_state(backend_module):
    backend_module.connection_manager.ensure_started()
    backend_module.connection_manager.reset_for_tests()
    yield
    backend_module.connection_manager.reset_for_tests()


@pytest.fixture
def backend_client(backend_module):
    return backend_module.app.test_client()
