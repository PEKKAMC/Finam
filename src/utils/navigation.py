# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

def navigate_to(page: ft.Page, route: str, disabled: bool = False) -> ft.EventHandler | None:
    if disabled:
        return None

    async def handler(e: ft.EventHandler | None = None) -> ft.EventHandler | None:
        await page.push_route(route)
        return e
    return handler