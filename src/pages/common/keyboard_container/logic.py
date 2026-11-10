# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import ast
from decimal import Decimal

from src.logger import Logger


def evaluate_expression(expression: str) -> str | None:
    """Evaluate the arithmetic operators supported by the amount keypad."""
    try:
        expression = expression.rstrip("+-*/.")
        if not expression:
            return None

        cleaned_expression = expression.replace("×", "*").replace("÷", "/")
        parsed_expression = ast.parse(cleaned_expression, mode="eval")
        def evaluate(node: ast.AST) -> Decimal:
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                literal = ast.get_source_segment(cleaned_expression, node)
                if literal is None:
                    raise ValueError("Could not read numeric literal")
                return Decimal(literal)
            if isinstance(node, ast.BinOp):
                left = evaluate(node.left)
                right = evaluate(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                if isinstance(node.op, ast.Div):
                    return left / right
                if isinstance(node.op, ast.Pow):
                    if right != right.to_integral_value():
                        raise ValueError("Money expressions require an integer exponent")
                    return left ** right
                if isinstance(node.op, ast.Mod):
                    return left % right
            if isinstance(node, ast.UnaryOp):
                operand = evaluate(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return +operand
                if isinstance(node.op, ast.USub):
                    return -operand
            raise ValueError("Unsupported expression element")

        result = evaluate(parsed_expression)
        if not result.is_finite():
            raise ValueError("Money expressions must produce a finite result")
        formatted = format(result, "f")
        return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted
    except Exception as error:
        Logger.error(f"Failed to evaluate expression '{expression}': {error}")
        return None
