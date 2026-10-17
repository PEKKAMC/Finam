# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from src.utils import Data


class LogicController:
    def __init__(self, user_info: dict):
        self.user_info = user_info

    @staticmethod
    def get_currencies() -> list:
        return Data().get_currencies()