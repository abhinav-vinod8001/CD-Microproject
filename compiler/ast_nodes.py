"""
Abstract Syntax Tree (AST) node definitions for the Malayalam Educational Compiler.
Each node supports hierarchical inspection, string formatting, and dictionary serialization.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, Union


class ASTNode(ABC):
    line: int = 1

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to a nested dictionary for UI tree visualization."""
        pass

    def to_str_tree(self, prefix: str = "", is_last: bool = True) -> str:
        """Render a clean ASCII tree representation."""
        marker = "└── " if is_last else "├── "
        result = prefix + marker + self._tree_label() + "\n"
        children = self._get_children()
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(children):
            result += child.to_str_tree(new_prefix, i == len(children) - 1)
        return result

    @abstractmethod
    def _tree_label(self) -> str:
        pass

    def _get_children(self) -> List["ASTNode"]:
        return []


class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements
        self.line = statements[0].line if statements else 1

    def _tree_label(self) -> str:
        return f"Program (Statements: {len(self.statements)})"

    def _get_children(self) -> List[ASTNode]:
        return self.statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Program",
            "name": f"Program [{len(self.statements)} stmts]",
            "children": [s.to_dict() for s in self.statements],
            "line": self.line,
        }


class AssignNode(ASTNode):
    def __init__(self, target: str, expr: ASTNode, line: int):
        self.target = target
        self.expr = expr
        self.line = line

    def _tree_label(self) -> str:
        return f"Assign: {self.target} ="

    def _get_children(self) -> List[ASTNode]:
        return [self.expr]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Assign",
            "name": f"Assign: {self.target}",
            "target": self.target,
            "children": [self.expr.to_dict()],
            "line": self.line,
        }


class PrintNode(ASTNode):
    def __init__(self, expressions: List[ASTNode], line: int):
        self.expressions = expressions
        self.line = line

    def _tree_label(self) -> str:
        return f"Print (കാണിക്കുക) [{len(self.expressions)} expr(s)]"

    def _get_children(self) -> List[ASTNode]:
        return self.expressions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Print",
            "name": "Print (കാണിക്കുക)",
            "children": [e.to_dict() for e in self.expressions],
            "line": self.line,
        }


class InputNode(ASTNode):
    def __init__(self, target: str, prompt: Optional[str] = None, line: int = 1):
        self.target = target
        self.prompt = prompt
        self.line = line

    def _tree_label(self) -> str:
        p = f' "{self.prompt}"' if self.prompt else ""
        return f"Input (വായിക്കുക) -> {self.target}{p}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Input",
            "name": f"Input (വായിക്കുക) -> {self.target}",
            "target": self.target,
            "prompt": self.prompt,
            "children": [],
            "line": self.line,
        }


class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None, line: int = 1):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []
        self.line = line

    def _tree_label(self) -> str:
        has_else = f" (with else: {len(self.else_body)} stmts)" if self.else_body else ""
        return f"If (എങ്കിൽ){has_else}"

    def _get_children(self) -> List[ASTNode]:
        children = [self.condition]
        children.extend(self.then_body)
        if self.else_body:
            children.extend(self.else_body)
        return children

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "If",
            "name": "If (എങ്കിൽ)",
            "children": [
                {
                    "type": "Condition",
                    "name": "Condition",
                    "children": [self.condition.to_dict()],
                },
                {
                    "type": "ThenBlock",
                    "name": "Then Block",
                    "children": [s.to_dict() for s in self.then_body],
                },
                *(
                    [{
                        "type": "ElseBlock",
                        "name": "Else Block (അല്ലെങ്കിൽ)",
                        "children": [s.to_dict() for s in self.else_body],
                    }]
                    if self.else_body else []
                ),
            ],
            "line": self.line,
        }


class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode], line: int = 1):
        self.condition = condition
        self.body = body
        self.line = line

    def _tree_label(self) -> str:
        return f"While (ആവർത്തിക്കുക) [{len(self.body)} stmts]"

    def _get_children(self) -> List[ASTNode]:
        return [self.condition] + self.body

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "While",
            "name": "While (ആവർത്തിക്കുക)",
            "children": [
                {
                    "type": "Condition",
                    "name": "Condition",
                    "children": [self.condition.to_dict()],
                },
                {
                    "type": "Body",
                    "name": "Loop Body",
                    "children": [s.to_dict() for s in self.body],
                },
            ],
            "line": self.line,
        }


class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def _tree_label(self) -> str:
        return f"BinaryOp: ({self.op})"

    def _get_children(self) -> List[ASTNode]:
        return [self.left, self.right]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOp",
            "name": f"BinaryOp: {self.op}",
            "op": self.op,
            "children": [self.left.to_dict(), self.right.to_dict()],
            "line": self.line,
        }


class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode, line: int):
        self.op = op
        self.operand = operand
        self.line = line

    def _tree_label(self) -> str:
        return f"UnaryOp: ({self.op})"

    def _get_children(self) -> List[ASTNode]:
        return [self.operand]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnaryOp",
            "name": f"UnaryOp: {self.op}",
            "op": self.op,
            "children": [self.operand.to_dict()],
            "line": self.line,
        }


class NumberNode(ASTNode):
    def __init__(self, value: Union[int, float], line: int):
        self.value = value
        self.line = line

    def _tree_label(self) -> str:
        return f"Number: {self.value}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Number",
            "name": f"Number: {self.value}",
            "value": self.value,
            "children": [],
            "line": self.line,
        }


class StringNode(ASTNode):
    def __init__(self, value: str, line: int):
        self.value = value
        self.line = line

    def _tree_label(self) -> str:
        return f'String: "{self.value}"'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "String",
            "name": f'String: "{self.value}"',
            "value": self.value,
            "children": [],
            "line": self.line,
        }


class BooleanNode(ASTNode):
    def __init__(self, value: bool, line: int):
        self.value = value
        self.line = line

    def _tree_label(self) -> str:
        val_mal = "ശരി" if self.value else "തെറ്റ്"
        return f"Boolean: {self.value} ({val_mal})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Boolean",
            "name": f"Boolean: {self.value}",
            "value": self.value,
            "children": [],
            "line": self.line,
        }


class VariableNode(ASTNode):
    def __init__(self, name: str, line: int):
        self.name = name
        self.line = line

    def _tree_label(self) -> str:
        return f"Variable: {self.name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Variable",
            "name": f"Variable: {self.name}",
            "variable": self.name,
            "children": [],
            "line": self.line,
        }


class InputExprNode(ASTNode):
    """Expression representing reading input, e.g. x = വായിക്കുക() or x = input()"""
    def __init__(self, prompt: Optional[str] = None, line: int = 1):
        self.prompt = prompt
        self.line = line

    def _tree_label(self) -> str:
        p = f' "{self.prompt}"' if self.prompt else ""
        return f"InputExpr (വായിക്കുക){p}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "InputExpr",
            "name": f"InputExpr (വായിക്കുക)",
            "prompt": self.prompt,
            "children": [],
            "line": self.line,
        }
