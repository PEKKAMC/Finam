# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os
import subprocess
import sys
import time
from typing import LiteralString

import flet as ft

from src.app import main as app
from src.logger import Logger
from src.version_manager import get_version

PACKAGE_NAME = "Finam"

def start_app(application: ft.AppCallable, assets_directory: LiteralString | str, app_version: str) -> int:
    restart_limit = int(os.getenv("FINAM_RESTART_LIMIT", "3"))
    restart_count = int(os.getenv("FINAM_RESTART_COUNT", "0"))

    if os.getenv("FINAM_CHILD") == "1":
        try:
            Logger.info(f"Starting Finam {app_version}...")
            ft.run(main=application, assets_dir=assets_directory)
            Logger.info("Finam closed gracefully.")
            return 0
        except Exception as e:
            Logger.critical(f"Application crashed: {e}", exc_info=True)
            return 1

    while True:
        env = os.environ.copy()
        env["FINAM_CHILD"] = "1"
        env["FINAM_RESTART_COUNT"] = str(restart_count)

        Logger.info(f"Launching Finam child process ({restart_count}/{restart_limit})...")
        proc = subprocess.Popen([sys.executable, os.path.realpath(__file__)], env=env)

        exit_code = proc.wait()

        if exit_code == 0:
            return 0

        if restart_count >= restart_limit:
            Logger.critical(f"Finam crashed {restart_count} times. Restart limit reached.")
            return exit_code

        restart_count += 1
        Logger.warning(f"Finam crashed with exit code {exit_code}. Restarting in 2s...")
        time.sleep(2)

def main() -> int:
    app_version = get_version(PACKAGE_NAME)
    assets_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src", "assets")

    if os.getenv("ENABLE_EDITOR") == "1":
        Logger.info("Lesson Editor enabled.")

    return start_app(app, assets_directory, app_version)

if __name__ == "__main__":
    raise SystemExit(main())