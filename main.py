# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import os

import flet as ft

from src.app import main as app
from src.logger import Logger
from src.version_manager import get_version

PACKAGE_NAME = "Finam"

def main() -> int:
    try:
        os.environ["RESTART_APP"] = "0"
        app_version = get_version(PACKAGE_NAME)
        assets_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")

        if os.getenv("ENABLE_EDITOR") == "1":
            Logger.info("Lesson Editor enabled.")

        # START APPLICATION
        Logger.info(f"Starting Finam {app_version}...")
        ft.run(app, assets_dir=assets_directory)

        # POST RUN CLEANUP
        if os.environ.get("RESTART_FINAM") == "1":
            Logger.info("Restarting...")
            return 1

        Logger.info("Finam closed gracefully.")
        return 0

    except Exception as e:
        Logger.critical(f"Application crashed: {e}", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        exit_code = main()
        if exit_code != 0:
            Logger.error("Application crashed twice, please restart manually...")

    exit(exit_code)