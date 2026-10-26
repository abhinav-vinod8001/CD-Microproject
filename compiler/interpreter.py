"""
Custom Interpreter and Virtual Machine for Malayalam Educational Programming Language.
Executes programs safely without eval() or exec(), maintaining a sandboxed environment,
step limit protection against infinite loops, input handling, and execution tracing.
"""

from typing import Dict, List, Any, Optional, Union
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


class InterpreterRuntimeError(Exception):
    def __init__(self, message: str, line: int = 1):
        self.message = message
        self.line = line
        super().__init__(f"Runtime Error at line {line}: {message}")


class InputRequiredException(Exception):
    def __init__(self, target: str, prompt: Optional[str] = None, line: int = 1):
        self.target = target
        self.prompt = prompt or f"Enter input for '{target}'"
        self.line = line
        super().__init__(f"Input required for '{target}' at line {line}")


class Interpreter:
    def __init__(self, max_steps: int = 50000):
        self.environment: Dict[str, Any] = {}
        self.output: List[str] = []
        self.trace: List[str] = []
        self.max_steps = max_steps
        self.steps = 0
        self.input_queue: List[str] = []

    def set_inputs(self, inputs: List[str]):
        """Queue inputs to be consumed by വായിക്കുക / input statements."""
        self.input_queue = list(inputs)

    def execute(self, program: ProgramNode, inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        self.environment.clear()
        self.output.clear()
        self.trace.clear()
        self.steps = 0
        if inputs is not None:
            self.set_inputs(inputs)

        for stmt in program.statements:
            self._execute_stmt(stmt)

        return {
            "output": "\n".join(self.output),
            "output_lines": list(self.output),
            "environment": dict(self.environment),
            "steps": self.steps,
            "trace": list(self.trace),
        }

    def _tick(self, line: int):
        self.steps += 1
        if self.steps > self.max_steps:
            raise InterpreterRuntimeError(
                f"Execution terminated: Exceeded maximum step limit ({self.max_steps}). Possible infinite loop detected.",
                line,
            )

    def _execute_stmt(self, node: ASTNode):
        self._tick(node.line)

        if isinstance(node, AssignNode):
            if isinstance(node.expr, InputExprNode):
                if node.expr.prompt:
                    self.output.append(node.expr.prompt)
                val = self._read_next_input(node.expr.prompt, node.line, target=node.target)
                self.output.append(str(val))
            else:
                val = self._eval_expr(node.expr)
            self.environment[node.target] = val
            self.trace.append(f"Line {node.line}: {node.target} = {val!r}")

        elif isinstance(node, PrintNode):
            out_parts = []
            for expr in node.expressions:
                val = self._eval_expr(expr)
                if isinstance(val, bool):
                    out_parts.append("true" if val else "false")
                elif isinstance(val, float) and val.is_integer():
                    out_parts.append(str(int(val)))
                else:
                    out_parts.append(str(val))
            line_out = " ".join(out_parts)
            self.output.append(line_out)
            self.trace.append(f"Line {node.line}: Output -> {line_out}")

        elif isinstance(node, InputNode):
            if node.prompt:
                self.output.append(node.prompt)
            val = self._read_next_input(node.prompt, node.line, target=node.target)
            self.output.append(str(val))
            self.environment[node.target] = val
            self.trace.append(f"Line {node.line}: Read {node.target} = {val!r}")

        elif isinstance(node, IfNode):
            cond_val = self._eval_expr(node.condition)
            self.trace.append(f"Line {node.line}: If condition evaluated to {bool(cond_val)}")
            if cond_val:
                for s in node.then_body:
                    self._execute_stmt(s)
            elif node.else_body:
                for s in node.else_body:
                    self._execute_stmt(s)

        elif isinstance(node, WhileNode):
            while True:
                self._tick(node.line)
                cond_val = self._eval_expr(node.condition)
                if not cond_val:
                    break
                for s in node.body:
                    self._execute_stmt(s)

    def _eval_expr(self, node: ASTNode) -> Any:
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, BooleanNode):
            return node.value

        if isinstance(node, VariableNode):
            if node.name not in self.environment:
                raise InterpreterRuntimeError(
                    f"Variable '{node.name}' has not been assigned a value before access.",
                    node.line,
                )
            return self.environment[node.name]

        if isinstance(node, InputExprNode):
            return self._read_next_input(node.prompt, node.line)

        if isinstance(node, UnaryOpNode):
            val = self._eval_expr(node.operand)
            if node.op == "-":
                if not isinstance(val, (int, float)):
                    raise InterpreterRuntimeError(f"Unary '-' cannot be applied to {type(val).__name__}", node.line)
                return -val
            elif node.op == "+":
                return val
            elif node.op == "not":
                return not bool(val)

        if isinstance(node, BinaryOpNode):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            op = node.op

            if op == "+":
                # String concatenation if either is string
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right

            elif op == "-":
                return left - right

            elif op == "*":
                if isinstance(left, str) and isinstance(right, int):
                    return left * right
                return left * right

            elif op == "/":
                if right == 0:
                    raise InterpreterRuntimeError("Division by zero error", node.line)
                res = left / right
                return int(res) if res.is_integer() else res

            elif op == "%":
                if right == 0:
                    raise InterpreterRuntimeError("Modulo by zero error", node.line)
                return left % right

            elif op == "==":
                return left == right

            elif op == "!=":
                return left != right

            elif op == "<":
                return left < right

            elif op == "<=":
                return left <= right

            elif op == ">":
                return left > right

            elif op == ">=":
                return left >= right

            elif op == "and":
                return bool(left and right)

            elif op == "or":
                return bool(left or right)

            raise InterpreterRuntimeError(f"Unsupported binary operator '{op}'", node.line)

        raise InterpreterRuntimeError(f"Unsupported AST node type '{type(node).__name__}'", getattr(node, "line", 1))

    def _read_next_input(self, prompt: Optional[str], line: int, target: str = "") -> Any:
        if self.input_queue:
            raw = self.input_queue.pop(0)
            raw_str = str(raw).strip()
            try:
                val_float = float(raw_str)
                return int(val_float) if val_float.is_integer() else val_float
            except ValueError:
                return raw_str

        # No input provided: signal that user input is required interactively
        raise InputRequiredException(target=target or "input", prompt=prompt, line=line)
