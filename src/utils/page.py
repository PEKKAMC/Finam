# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger


class Page(ft.Page):
    def navigate_to(self, route: str):
        async def handler(e: ft.ControlEvent) -> ft.ControlEvent | None:
            try:
                await self.push_route(route)
            except Exception as ex_push_route:
                Logger.error(f"Failed to navigate to {route} through push_route(), using go() instead: {ex_push_route}")
                try:
                    self.go(route)
                except Exception as ex_go:
                    Logger.error(f"Failed to navigate to {route} through go(): {ex_go}")
            return e

        return handler


ft.Page.navigate_to = Page.navigate_to