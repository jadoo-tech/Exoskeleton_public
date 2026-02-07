from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = REPO_ROOT / "Server" / "Web Page" / "backend"


def _close_client_maps(app_module: object) -> None:
    for mapping_name in ("clients_exec", "clients_video"):
        mapping = getattr(app_module, mapping_name)
        for conn, _addr in list(mapping.values()):
            try:
                conn.close()
            except OSError:
                pass
        mapping.clear()


@pytest.fixture(scope="session")
def backend_module():
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))

    constants = importlib.import_module("constants")
    constants.HOST = "127.0.0.1"

    original_cwd = os.getcwd()
    os.chdir(BACKEND_DIR)

    app_module = importlib.import_module("app")
    yield app_module

    _close_client_maps(app_module)
    app_module.latest_frames.clear()

    for sock_name in ("sock_exec", "sock_video"):
        sock = getattr(app_module, sock_name)
        try:
            sock.close()
        except OSError:
            pass

    os.chdir(original_cwd)


@pytest.fixture(autouse=True)
def reset_backend_state(backend_module):
    _close_client_maps(backend_module)
    backend_module.latest_frames.clear()
    yield
    _close_client_maps(backend_module)
    backend_module.latest_frames.clear()


@pytest.fixture
def backend_client(backend_module):
    return backend_module.app.test_client()
