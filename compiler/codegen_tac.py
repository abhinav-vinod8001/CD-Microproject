"""
Three-Address Code (TAC) Intermediate Representation (IR) Generator.
Translates AST into standard compiler-design TAC instructions (quadruples).
"""

from typing import List, Optional, Any, Dict
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


class TACInstruction:
    def __init__(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, result: Optional[str] = None, comment: str = ""):
        self.op = op          # e.g. '=', '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', 'and', 'or', 'not', 'LABEL', 'GOTO', 'IF_FALSE', 'IF_TRUE', 'PRINT', 'READ'
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        self.comment = comment

    def to_str(self) -> str:
        if self.op == "LABEL":
            return f"{self.result}:"
        elif self.op == "GOTO":
            return f"goto {self.result}"
        elif self.op == "IF_FALSE":
            return f"if_false {self.arg1} goto {self.result}"
        elif self.op == "IF_TRUE":
            return f"if_true {self.arg1} goto {self.result}"
        elif self.op == "PRINT":
            return f"print {self.arg1}"
        elif self.op == "READ":
            prompt_str = f', "{self.arg2}"' if self.arg2 else ""
            return f"read {self.result}{prompt_str}"
        elif self.op == "=":
            return f"{self.result} = {self.arg1}"
        elif self.op in ("not", "neg"):
            return f"{self.result} = {self.op} {self.arg1}"
        else:
            # Binary operations
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": self.op,
            "arg1": str(self.arg1) if self.arg1 is not None else None,
            "arg2": str(self.arg2) if self.arg2 is not None else None,
            "result": str(self.result) if self.result is not None else None,
            "representation": self.to_str(),
            "comment": self.comment,
        }

    def __repr__(self) -> str:
        return self.to_str()


class TACGenerator:
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self._temp_count = 0
        self._label_count = 0

    def new_temp(self) -> str:
        name = f"t{self._temp_count}"
        self._temp_count += 1
        return name

    def new_label(self) -> str:
        name = f"L{self._label_count}"
        self._label_count += 1
        return name

    def generate(self, program: ProgramNode) -> List[TACInstruction]:
        self.instructions.clear()
        self._temp_count = 0
        self._label_count = 0

        for stmt in program.statements:
            self._gen_stmt(stmt)

        return list(self.instructions)

    def _emit(self, op: str, arg1: Optional[str] = None, arg2: Optional[str] = None, result: Optional[str] = None, comment: str = ""):
        inst = TACInstruction(op, arg1, arg2, result, comment)
        self.instructions.append(inst)
        return inst

    def _gen_stmt(self, node: ASTNode):
        if isinstance(node, AssignNode):
            val = self._gen_expr(node.expr)
            self._emit("=", arg1=val, result=node.target, comment=f"Assign to {node.target}")

        elif isinstance(node, PrintNode):
            for expr in node.expressions:
                val = self._gen_expr(expr)
                self._emit("PRINT", arg1=val, comment="Output expression")

        elif isinstance(node, InputNode):
            self._emit("READ", arg2=node.prompt, result=node.target, comment="Read into variable")

        elif isinstance(node, IfNode):
            cond_val = self._gen_expr(node.condition)
            else_label = self.new_label()
            end_label = self.new_label()

            # If condition is false, jump to else (or end if no else)
            target_false = else_label if node.else_body else end_label
            self._emit("IF_FALSE", arg1=cond_val, result=target_false, comment="Jump if false")

            # Then block
            for s in node.then_body:
                self._gen_stmt(s)

            if node.else_body:
                self._emit("GOTO", result=end_label, comment="Skip else branch")
                self._emit("LABEL", result=else_label, comment="Else label")
                for s in node.else_body:
                    self._gen_stmt(s)
                self._emit("LABEL", result=end_label, comment="End if label")
            else:
                self._emit("LABEL", result=end_label, comment="End if label")

        elif isinstance(node, WhileNode):
            start_label = self.new_label()
            end_label = self.new_label()

            self._emit("LABEL", result=start_label, comment="While loop start")
            cond_val = self._gen_expr(node.condition)
            self._emit("IF_FALSE", arg1=cond_val, result=end_label, comment="Exit loop if false")

            # Body
            for s in node.body:
                self._gen_stmt(s)

            self._emit("GOTO", result=start_label, comment="Repeat loop")
            self._emit("LABEL", result=end_label, comment="While loop end")

    def _gen_expr(self, node: ASTNode) -> str:
        if isinstance(node, NumberNode):
            return str(node.value)

        if isinstance(node, StringNode):
            # Enclose in quotes
            return repr(node.value)

        if isinstance(node, BooleanNode):
            return "true" if node.value else "false"

        if isinstance(node, VariableNode):
            return node.name

        if isinstance(node, InputExprNode):
            temp = self.new_temp()
            self._emit("READ", arg2=node.prompt, result=temp, comment="Read input into temp")
            return temp

        if isinstance(node, UnaryOpNode):
            val = self._gen_expr(node.operand)
            temp = self.new_temp()
            op = "neg" if node.op == "-" else ("not" if node.op == "not" else node.op)
            self._emit(op, arg1=val, result=temp)
            return temp

        if isinstance(node, BinaryOpNode):
            left_val = self._gen_expr(node.left)
            right_val = self._gen_expr(node.right)
            temp = self.new_temp()
            self._emit(node.op, arg1=left_val, arg2=right_val, result=temp)
            return temp

        temp = self.new_temp()
        self._emit("=", arg1="0", result=temp)
        return temp
