# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.


def get_user_initial(username: str) -> str:
    """Get the uppercase first character used in a user avatar."""
    return username[0].upper() if username else ""


def format_created_date_label(prefix: str, created_at: str) -> str:
    """Format the account creation date, including its unavailable state."""
    return f"{prefix} {created_at}" if created_at else f"{prefix} --"
