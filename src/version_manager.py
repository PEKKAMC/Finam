# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from importlib.metadata import version

from src.logger import Logger

def get_version(package: str, rc: int = 0) -> str:
    try:
        app_version = version(package)
        nversion: list[int] = list(map(int, app_version.split('.')))
        if len(nversion) != 3:
            raise RuntimeError(f"Invalid version format, must be in the format of X.Y.Z, got {app_version}")
    except Exception as e:
        Logger.error(f"Error occurred while fetching version for {package}: {e}")
        return "version-undefined"

    version_suffix = ""

    if nversion[0] == 0:
        version_suffix = "-alpha"
    elif rc > 0:
        version_suffix = f"-rc{rc}"

    final_version = f"v{app_version}{version_suffix}"
    return final_version
