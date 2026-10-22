# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import importlib
from importlib.metadata import version
from typing import Optional

from src.logger import Logger

APP_VERSION: Optional[str] = None
try:
    _build_version = importlib.import_module("src._build_version")
    # noinspection PyGlobalVariableRedeclarationInNotebook
    APP_VERSION = getattr(_build_version, "APP_VERSION", None)
except (ImportError, ModuleNotFoundError):
    pass


def get_version(package: str, rc: int = 0) -> str:
    try:
        if APP_VERSION is not None:
            app_version = APP_VERSION
        else:
            app_version = version(package)

        nversion: list[int] = list(map(int, app_version.split('.')))
        if len(nversion) != 3:
            raise ValueError(f"Invalid version format, must be in the format of X.Y.Z, got {app_version}")
    except Exception as ex:
        Logger.error(f"Error occurred while fetching version for {package}: {ex}")
        return "version-undefined"

    version_suffix = ""

    if nversion[0] == 0:
        if 0 <= nversion[1] <= 2:
            version_suffix = "-alpha"
        elif nversion[1] >= 3:
            version_suffix = "-beta"

    elif rc > 0:
        version_suffix = f"-rc{rc}"

    return f"v{app_version}{version_suffix}"