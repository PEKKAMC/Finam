# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re
from typing import TypedDict

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$"
)


class HelpFormValidation(TypedDict):
    is_valid: bool
    field_errors: dict[str, bool]
    email_error_key: str


class HelpFormLogic:
    @staticmethod
    def validate_submission(name: str, email: str, subject: str, message: str) -> HelpFormValidation:
        normalized_email = email.strip()
        field_errors = {
            "name": not name.strip(),
            "email": not normalized_email,
            "subject": not subject.strip(),
            "message": not message.strip(),
        }
        # Validation is kept independent of Flet so input rules can be checked without building UI.
        email_is_invalid = bool(normalized_email) and not EMAIL_PATTERN.fullmatch(
            normalized_email
        )
        field_errors["email"] = field_errors["email"] or email_is_invalid
        has_errors = any(field_errors.values())

        return {
            "is_valid": not has_errors,
            "field_errors": field_errors,
            "email_error_key": (
                "help.form_required"
                if not normalized_email
                else "help.form_invalid_email"
            ),
        }
