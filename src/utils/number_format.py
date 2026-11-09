    # Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import math
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


def format_compact_number(value: float, decimals: int = 1, signed: bool = False, translations: dict[str, str] | None = None) -> str:
    """Format large values with a compact magnitude suffix."""
    suffixes = (
        ("thousand", "K"),
        ("million", "M"),
        ("billion", "B"),
        ("trillion", "T"),
        ("quadrillion", "Qa"),
        ("quintillion", "Qi"),
        ("sextillion", "Sx"),
        ("septillion", "Sp"),
        ("octillion", "Oc"),
        ("nonillion", "No"),
        ("decillion", "Dc"),
    )
    magnitude_suffixes = ("",) + tuple(
        translations.get(f"number_suffix.{key}", fallback)
        if translations
        else fallback
        for key, fallback in suffixes
    )
    absolute_value = abs(value)
    if not math.isfinite(value) or absolute_value < 1_000:
        return format_number(value, signed=signed)

    magnitude = min(
        len(magnitude_suffixes) - 1,
        int(math.log10(absolute_value) // 3),
    )
    scaled_value = value / (1_000 ** magnitude)

    while (
        magnitude < len(magnitude_suffixes) - 1
        and round(abs(scaled_value), decimals) >= 1_000
    ):
        magnitude += 1
        scaled_value /= 1_000

    formatted = format_number(scaled_value, decimals=decimals, signed=signed)
    if _decimal_separator in formatted:
        formatted = formatted.rstrip("0").rstrip(_decimal_separator)
    return f"{formatted}{magnitude_suffixes[magnitude]}"


def format_display_number(value: float, translations: dict[str, str], decimals: int = 1, signed: bool = False) -> str:
    """Keep up to 12 integer digits unabridged and localize larger values."""
    if not math.isfinite(value):
        return format_number(value, signed=signed)
    if len(str(int(abs(value)))) <= 12:
        return format_number(value, signed=signed)
    return format_compact_number(
        value,
        decimals=decimals,
        signed=signed,
        translations=translations,
    )


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
