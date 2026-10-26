"""
Semantic Analyzer and Symbol Table for the Malayalam Educational Compiler.
Performs symbol definition tracking, undeclared identifier detection,
static type inference, and diagnostic warning/error checks.
"""

from typing import Dict, List, Any, Optional, Set
from .ast_nodes import (
    ASTNode,
    ProgramNode,
    AssignNode,
    PrintNode,
    InputNode,
    IfNode,
    WhileNode,
    BinaryOpNode,
    UnaryOpNode,
    NumberNode,
    StringNode,
    BooleanNode,
    VariableNode,
    InputExprNode,
)


class SemanticError(Exception):
    def __init__(self, message: str, line: int = 1):
        self.message = message
        self.line = line
        super().__init__(f"Semantic Error at line {line}: {message}")


class SymbolEntry:
    def __init__(self, name: str, inferred_type: str, line_defined: int, scope: str = "global"):
        self.name = name
        self.inferred_type = inferred_type
        self.line_defined = line_defined
        self.scope = scope
        self.initialized = True
        self.references: List[int] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.inferred_type,
            "scope": self.scope,
            "line_defined": self.line_defined,
            "initialized": self.initialized,
            "references": self.references,
        }


class Diagnostic:
    def __init__(self, severity: str, message: str, line: int):
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
        self.line = line

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
        }


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table: Dict[str, SymbolEntry] = {}
        self.diagnostics: List[Diagnostic] = []

    def analyze(self, program: ProgramNode) -> Dict[str, Any]:
        self.symbol_table.clear()
        self.diagnostics.clear()

        # Traverse statements
        for stmt in program.statements:
            self._visit_stmt(stmt)

        # Check for unused variables (warning)
        for name, entry in self.symbol_table.items():
            if not entry.references:
                self.diagnostics.append(
                    Diagnostic("warning", f"Variable '{name}' is defined at line {entry.line_defined} but never used.", entry.line_defined)
                )

        return {
            "symbol_table": [entry.to_dict() for entry in self.symbol_table.values()],
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "has_errors": any(d.severity == "error" for d in self.diagnostics),
        }

    def _visit_stmt(self, node: ASTNode):
        if isinstance(node, AssignNode):
            expr_type = self._infer_expr_type(node.expr)
            if node.target not in self.symbol_table:
                self.symbol_table[node.target] = SymbolEntry(
                    name=node.target,
                    inferred_type=expr_type,
                    line_defined=node.line,
                )
            else:
                # Update existing inferred type if refined
                if expr_type != "unknown":
                    self.symbol_table[node.target].inferred_type = expr_type

        elif isinstance(node, InputNode):
            if node.target not in self.symbol_table:
                self.symbol_table[node.target] = SymbolEntry(
                    name=node.target,
                    inferred_type="dynamic",
                    line_defined=node.line,
                )

        elif isinstance(node, PrintNode):
            for expr in node.expressions:
                self._infer_expr_type(expr)

        elif isinstance(node, IfNode):
            cond_type = self._infer_expr_type(node.condition)
            for stmt in node.then_body:
                self._visit_stmt(stmt)
            for stmt in node.else_body:
                self._visit_stmt(stmt)

        elif isinstance(node, WhileNode):
            cond_type = self._infer_expr_type(node.condition)
            # Static check for infinite loop / false condition
            if isinstance(node.condition, BooleanNode) and not node.condition.value:
                self.diagnostics.append(
                    Diagnostic("warning", f"While loop condition is always false at line {node.line}. Loop body will not execute.", node.line)
                )
            for stmt in node.body:
                self._visit_stmt(stmt)

    def _infer_expr_type(self, node: ASTNode) -> str:
        if isinstance(node, NumberNode):
            return "float" if isinstance(node.value, float) else "int"

        if isinstance(node, StringNode):
            return "string"

        if isinstance(node, BooleanNode):
            return "bool"

        if isinstance(node, InputExprNode):
            return "dynamic"

        if isinstance(node, VariableNode):
            if node.name not in self.symbol_table:
                msg = f"Variable '{node.name}' is used before declaration or assignment."
                self.diagnostics.append(Diagnostic("error", msg, node.line))
                raise SemanticError(msg, node.line)
            else:
                self.symbol_table[node.name].references.append(node.line)
                return self.symbol_table[node.name].inferred_type

        if isinstance(node, UnaryOpNode):
            operand_type = self._infer_expr_type(node.operand)
            if node.op == "not":
                return "bool"
            return operand_type

        if isinstance(node, BinaryOpNode):
            left_type = self._infer_expr_type(node.left)
            right_type = self._infer_expr_type(node.right)

            # Check division by zero literal
            if node.op in ("/", "%") and isinstance(node.right, NumberNode) and node.right.value == 0:
                msg = f"Division or modulo by zero detected in expression at line {node.line}."
                self.diagnostics.append(Diagnostic("error", msg, node.line))
                raise SemanticError(msg, node.line)

            # Arithmetic ops
            if node.op in ("+", "-", "*", "/", "%"):
                if node.op == "+":
                    if left_type == "string" or right_type == "string":
                        return "string"  # Concatenation
                if left_type == "float" or right_type == "float" or node.op == "/":
                    return "float"
                if left_type == "int" and right_type == "int":
                    return "int"
                return "number"

            # Comparison and logical ops
            if node.op in ("==", "!=", "<", ">", "<=", ">=", "and", "or"):
                return "bool"

            return "unknown"

        return "unknown"
