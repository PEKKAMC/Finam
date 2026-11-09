# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import ast
import math

from src.logger import Logger


def evaluate_expression(expression: str) -> str | None:
    """Evaluate the arithmetic operators supported by the amount keypad."""
    try:
        expression = expression.rstrip("+-*/.")
        if not expression:
            return None

        cleaned_expression = expression.replace("×", "*").replace("÷", "/")
        parsed_expression = ast.parse(cleaned_expression, mode="eval")
        allowed_binary_operators = (
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Pow,
            ast.Mod,
        )
        allowed_unary_operators = (ast.UAdd, ast.USub)

        for node in ast.walk(parsed_expression):
            if isinstance(node, ast.BinOp):
                if not isinstance(node.op, allowed_binary_operators):
                    raise ValueError("Unsupported arithmetic operator")
            elif isinstance(node, ast.UnaryOp):
                if not isinstance(node.op, allowed_unary_operators):
                    raise ValueError("Unsupported unary operator")
            elif isinstance(node, ast.Constant):
                if not isinstance(node.value, (int, float)):
                    raise ValueError("Only numeric values are allowed")
            elif isinstance(
                node,
                (*allowed_binary_operators, *allowed_unary_operators, ast.Expression),
            ):
                continue
            else:
                raise ValueError("Unsupported expression element")

        result = eval(
            compile(parsed_expression, "<amount-expression>", "eval"),
            {"__builtins__": {}},
            {"math": math},
        )
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except Exception as error:
        Logger.error(f"Failed to evaluate expression '{expression}': {error}")
        return None
