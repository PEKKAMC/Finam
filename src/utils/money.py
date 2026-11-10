# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from decimal import Decimal, InvalidOperation

type Money = Decimal


def to_decimal(value: Decimal | int | str) -> Decimal:
    """Convert a monetary value without introducing binary floating-point rounding."""
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise TypeError(f"Unsupported monetary value: {type(value).__name__}")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"Invalid monetary amount: {value!r}") from error
    if not result.is_finite():
        raise ValueError("Monetary amounts must be finite")
    return result
