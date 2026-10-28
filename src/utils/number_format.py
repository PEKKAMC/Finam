# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import re


_digit_separator = ""
_decimal_separator = "."
_VALID_SEPARATORS = {"", ".", ",", "_"}
_VALID_DECIMAL_SEPARATORS = {".", ","}


def set_digit_separator(separator: str) -> None:
    if separator not in _VALID_SEPARATORS:
        raise ValueError(f"Unsupported digit separator: {separator!r}")
    global _digit_separator
    _digit_separator = separator


def set_decimal_separator(separator: str) -> None:
    if separator not in _VALID_DECIMAL_SEPARATORS:
        raise ValueError(f"Unsupported decimal separator: {separator!r}")
    global _decimal_separator
    _decimal_separator = separator


def get_decimal_separator() -> str:
    return _decimal_separator


def format_number(value: float, decimals: int = 2, signed: bool = False) -> str:
    formatted = f"{value:{'+' if signed else ''},.{decimals}f}"
    integer, decimal, fraction = formatted.partition(".")
    if _digit_separator:
        integer = integer.replace(",", _digit_separator)
    else:
        integer = integer.replace(",", "")
    return integer + (_decimal_separator + fraction if decimal else "")


def format_expression(expression: str) -> str:
    def format_literal(match: re.Match[str]) -> str:
        literal = match.group()
        integer, decimal, fraction = literal.partition(".")
        grouped = integer
        if _digit_separator and len(integer) > 3:
            first_group_size = len(integer) % 3 or 3
            groups = [integer[:first_group_size]]
            groups.extend(
                integer[index:index + 3]
                for index in range(first_group_size, len(integer), 3)
            )
            grouped = _digit_separator.join(groups)
        return grouped + (_decimal_separator + fraction if decimal else "")

    return re.sub(r"\d+(?:\.\d*)?", format_literal, expression)
