from __future__ import annotations

import subprocess
import sys
import threading
import time

import constants


threads: list[threading.Thread] = []


def run_task(script: str) -> None:
    subprocess.run([sys.executable, script], check=False)


if __name__ == "__main__":
    print(
        f"Starting client stack mode={constants.COMM_STACK}, scripts={constants.SCRIPTS}"
    )
    for script in constants.SCRIPTS:
        thread = threading.Thread(target=run_task, args=(script,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Main thread interrupted. Exiting...")
