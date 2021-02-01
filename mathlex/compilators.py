# © vidmartin 2021

from __future__ import annotations

from typing import *
import math

from .mathlex import *
from .nodes import *

def compileCompare(tokens: List[Token]) -> Optional[Node]: 
    for i in range(len(tokens)):
        i = len(tokens) - 1 - i
        token = tokens[i]
        if token.kind == "operator" and token.data in ("<", ">", "<=", ">=", "!=", "==", "=", "/=", "=/="):
            left = compileNode(tokens[:i])
            right = compileNode(tokens[i+1:])
            if left == None or right == None:
                return None

            if token.data in ("=", "=="):
                return CompareNode(left, right, lambda a, b: a == b)
            elif token.data in ("!=", "/=", "=/="):
                return CompareNode(left, right, lambda a, b: a != b)
            elif token.data == ">":
                return CompareNode(left, right, lambda a, b: a > b)
            elif token.data == ">=":
                return CompareNode(left, right, lambda a, b: a >= b)
            elif token.data == "<":
                return CompareNode(left, right, lambda a, b: a < b)
            elif token.data == "<=":
                return CompareNode(left, right, lambda a, b: a <= b)

def compilePlusMinus(tokens: List[Token]) -> Optional[Node]:
    for i in range(len(tokens) - 1):
        i = len(tokens) - 1 - i # odzadu
        token = tokens[i]
        if token.kind == "operator" and token.data in ("+", "-"):
            left = compileNode(tokens[:i])
            right = compileNode(tokens[i+1:])
            if left == None or right == None:
                return None

            if token.data == "+":
                return BinaryNode(left, right, lambda a, b: a + b)
            else:
                return BinaryNode(left, right, lambda a, b: a - b)

def compileMultiplyDivide(tokens: List[Token]) -> Optional[Node]:
    for i in range(len(tokens) - 1):
        i = len(tokens) - 1 - i # odzadu
        token = tokens[i]
        if token.kind == "operator" and token.data in ("*", "/"):
            left = compileNode(tokens[:i])
            right = compileNode(tokens[i+1:])
            if left == None or right == None:
                return None

            if token.data == "*":
                return BinaryNode(left, right, lambda a, b: a * b)
            else:
                return BinaryNode(left, right, lambda a, b: a / b)

def compilePower(tokens: List[Token]) -> Optional[Node]:
    for i in range(len(tokens) - 1):
        i = len(tokens) - 1 - i # odzadu
        token = tokens[i]
        if token.kind == "operator" and token.data == "^":
            left = compileNode(tokens[:i])
            right = compileNode(tokens[i+1:])
            return BinaryNode(left, right, lambda a, b,: a ** b)

UNARY_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "atan": math.atan,
    "asin": math.asin,
    "acos": math.acos,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil
}

def compileFunction(tokens: List[Token]) -> Optional[Node]:
    if len(tokens) == 2 and tokens[0].kind == "word" and tokens[0].data.lower() in UNARY_FUNCTIONS and tokens[1].kind == "subexpr":
        return UnaryNode(compileNode(tokens[1].data), UNARY_FUNCTIONS[tokens[0].data.lower()])

def compileSubexpression(tokens: List[Token]) -> Optional[Node]:
    if len(tokens) == 1 and tokens[0].kind == "subexpr":
        return compileNode(tokens[0].data)

def compileConstant(tokens: List[Token]) -> Optional[Node]:
    if len(tokens) == 1 and tokens[0].kind == "number":
        return ConstantNode(tokens[0].data)
    if len(tokens) == 2 and tokens[0].kind == "operator" and tokens[0].data in ("+", "-") and tokens[1].kind == "number":
        return ConstantNode(tokens[1].data * (-1 if tokens[0].data == "-" else 1))

COMPILE_ORDER_CALCULATOR = [
    compilePlusMinus,
    compileMultiplyDivide,
    compilePower,
    compileFunction,
    compileSubexpression,
    compileConstant
]

COMPILE_ORDER_WITH_COMPARE = [
    compileCompare,
    compilePlusMinus,
    compileMultiplyDivide,
    compilePower,
    compileFunction,
    compileSubexpression,
    compileConstant
]

def compileNode(tokens: List[Token], compileOrder: List[Callable[[List[Token]], Optional[Node]]] = None) -> Optional[Node]:
    if compileOrder == None:
        compileOrder = COMPILE_ORDER_CALCULATOR

    for compilator in compileOrder:
        node = compilator(tokens)
        if node:
            return node