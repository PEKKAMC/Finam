# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger


_original_control_update = ft.Control.update


def _safe_control_update(self):
    """Ignore detached-control updates until the control is actually attached to a page."""
    try:
        if self is None:
            return None

        page_ref = getattr(self, "page", None)
        if page_ref is None:
            return None

        return _original_control_update(self)
    except Exception as exc:  # pragma: no cover - Flet raises this before page attaches in some race cases
        message = str(exc).lower()
        if "must be added to the page" in message or "no element" in message:
            Logger.debug(f"Skipping control update for detached control: {exc}")
            return None
        raise


ft.Control.update = _safe_control_update


class Page(ft.Page):
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