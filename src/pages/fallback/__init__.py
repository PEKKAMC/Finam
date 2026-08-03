# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Fallback page - For unsupported screens or broken routing."""

from src.pages.fallback.components import NotSupportedMessageBox, ReturnButton
from src.pages.fallback.view import FallbackView, get_fallback_view


__all__ = [
    "NotSupportedMessageBox",
    "ReturnButton",
    "FallbackView",
    "get_fallback_view"
]

