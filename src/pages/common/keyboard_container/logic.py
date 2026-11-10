# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import ast
import operator
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
        binary_operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }
        unary_operations = {ast.UAdd: operator.pos, ast.USub: operator.neg}

        def evaluate(node: ast.AST) -> Decimal:
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                literal = ast.get_source_segment(cleaned_expression, node)
                if literal is None:
                    raise ValueError("Could not read numeric literal")
                return Decimal(literal)
            if isinstance(node, ast.BinOp) and type(node.op) in binary_operations:
                left = evaluate(node.left)
                right = evaluate(node.right)
                if isinstance(node.op, ast.Pow) and right != right.to_integral_value():
                    raise ValueError("Money expressions require an integer exponent")
                return binary_operations[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and type(node.op) in unary_operations:
                return unary_operations[type(node.op)](evaluate(node.operand))
            raise ValueError("Unsupported expression element")

        result = evaluate(parsed_expression)
        if not result.is_finite():
            raise ValueError("Money expressions must produce a finite result")
        formatted = format(result, "f")
        return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted
    except Exception as error:
        Logger.error(f"Failed to evaluate expression '{expression}': {error}")
        return None
