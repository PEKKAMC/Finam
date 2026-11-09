# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


def get_active_menu_item(route: str) -> str:
    """Return the navigation item matching the current route."""
    match route:
        case "/user_management":
            return "user_management"
        case "/home":
            return "home"
        case "/lessons" | "/lesson-player":
            return "lesson"
        case "/savings":
            return "saving"
        case "/spending":
            return "spending"
        case "/purchase_scanner":
            return "scanner"
        case "/lesson-editor":
            return "editor"
        case _:
            return ""
