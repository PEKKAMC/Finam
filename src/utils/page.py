# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from collections.abc import Callable

import flet as ft

from src.logger import Logger


class Page(ft.Page):
    def __init__(self):
        self.delete_cached_view: Callable
        self.delete_all_cached_views: Callable
        self.pending_objective_id: int | None

    def navigate_to(self, route: str):
        def handler(e: ft.ControlEvent | None = None) -> None:
            try:
                normalized_route = str(route or "")
                current_route = str(self.route or "")
                if normalized_route == current_route:
                    Logger.info(f"Skipping route navigation to '{normalized_route}' because we are already there.")
                    return
                self.run_task(self.push_route, normalized_route)
            except Exception as ex:
                Logger.error(f"Failed to navigate to {route}: {ex}\nEvent details: {e}")

        return handler


setattr(ft.Page, "navigate_to", Page.navigate_to)