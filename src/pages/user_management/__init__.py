# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""User management page - User management and settings."""

from src.pages.global_components.user_dialog import AddUserField, DeleteUserDialog, UserList, UserManagementDialog
from src.pages.user_management.components import GoogleAccountCard, MenuItem, MenuSectionCard, ProfileCard, DeleteAllDataDialog
from src.pages.user_management.logic import LogicController
from src.pages.user_management.view import (
    DialogManager,
    UserManagementView,
    complete_google_web_callback,
    get_user_management_view,
)

__all__ = [
    "AddUserField",
    "DeleteUserDialog",
    "MenuItem",
    "MenuSectionCard",
    "ProfileCard",
    "GoogleAccountCard",
    "DeleteAllDataDialog",
    "UserList",
    "UserManagementDialog",
    "LogicController",
    "DialogManager",
    "UserManagementView",
    "complete_google_web_callback",
    "get_user_management_view"
]