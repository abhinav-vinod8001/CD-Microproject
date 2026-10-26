"""
Optimizer for Three-Address Code (TAC).
Performs Constant Folding, Algebraic Simplifications, Constant Propagation,
and Redundant Temporary Elimination.
"""

from typing import List, Tuple, Dict, Any, Optional
from .codegen_tac import TACInstruction


def is_number(val: Optional[str]) -> bool:
    if val is None:
        return False
    try:
        float(val)
        return True
    except ValueError:
        return False


def parse_number(val: str):
    f = float(val)
    return int(f) if f.is_integer() else f


def is_string_literal(val: Optional[str]) -> bool:
    if val is None:
        return False
    return (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'"))


def parse_string(val: str) -> str:
    return val[1:-1]


class Optimizer:
    def __init__(self):
        self.logs: List[str] = []

    def optimize(self, instructions: List[TACInstruction]) -> Tuple[List[TACInstruction], List[str]]:
        self.logs.clear()
        current = [
            TACInstruction(inst.op, inst.arg1, inst.arg2, inst.result, inst.comment)
            for inst in instructions
        ]

        # Multi-pass optimization until fixed point or max 5 passes
        changed = True
        passes = 0
        while changed and passes < 5:
            passes += 1
            changed = False

            # Pass 1: Constant folding & algebraic simplification
            folded_list: List[TACInstruction] = []
            for inst in current:
                optimized_inst, log_msg = self._optimize_instruction(inst)
                if log_msg:
                    self.logs.append(log_msg)
                    changed = True
                folded_list.append(optimized_inst)

            # Pass 2: Redundant temporary forwarding (e.g. t0 = 30, x = t0 -> x = 30)
            forwarded_list, fw_changed = self._forward_temporaries(folded_list)
            if fw_changed:
                changed = True

            current = forwarded_list

        return current, self.logs

    def _optimize_instruction(self, inst: TACInstruction) -> Tuple[TACInstruction, Optional[str]]:
        # Constant folding for binary arithmetic on numeric literals
        if inst.op in ("+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=") and inst.arg1 and inst.arg2:
            if is_number(inst.arg1) and is_number(inst.arg2):
                n1 = parse_number(inst.arg1)
                n2 = parse_number(inst.arg2)
                res = None

                try:
                    if inst.op == "+":
                        res = n1 + n2
                    elif inst.op == "-":
                        res = n1 - n2
                    elif inst.op == "*":
                        res = n1 * n2
                    elif inst.op == "/":
                        if n2 != 0:
                            f = n1 / n2
                            res = int(f) if f.is_integer() else f
                    elif inst.op == "%":
                        if n2 != 0:
                            res = n1 % n2
                    elif inst.op == "==":
                        res = "true" if n1 == n2 else "false"
                    elif inst.op == "!=":
                        res = "true" if n1 != n2 else "false"
                    elif inst.op == "<":
                        res = "true" if n1 < n2 else "false"
                    elif inst.op == ">":
                        res = "true" if n1 > n2 else "false"
                    elif inst.op == "<=":
                        res = "true" if n1 <= n2 else "false"
                    elif inst.op == ">=":
                        res = "true" if n1 >= n2 else "false"
                except Exception:
                    res = None

                if res is not None:
                    old_rep = inst.to_str()
                    val_str = str(res) if not isinstance(res, str) else res
                    new_inst = TACInstruction("=", arg1=val_str, result=inst.result, comment=inst.comment)
                    return new_inst, f"Constant Folding: '{old_rep}' -> '{new_inst.to_str()}'"

            # String concatenation folding
            if inst.op == "+" and is_string_literal(inst.arg1) and is_string_literal(inst.arg2):
                s1 = parse_string(inst.arg1)
                s2 = parse_string(inst.arg2)
                combined = repr(s1 + s2)
                old_rep = inst.to_str()
                new_inst = TACInstruction("=", arg1=combined, result=inst.result, comment=inst.comment)
                return new_inst, f"Constant Folding: '{old_rep}' -> '{new_inst.to_str()}'"

            # Algebraic simplifications
            # x + 0 -> x
            if inst.op == "+":
                if inst.arg2 == "0":
                    return TACInstruction("=", arg1=inst.arg1, result=inst.result), f"Algebraic Simplification: '{inst.to_str()}' -> '{inst.result} = {inst.arg1}'"
                if inst.arg1 == "0":
                    return TACInstruction("=", arg1=inst.arg2, result=inst.result), f"Algebraic Simplification: '{inst.to_str()}' -> '{inst.result} = {inst.arg2}'"

            # x - 0 -> x
            if inst.op == "-" and inst.arg2 == "0":
                return TACInstruction("=", arg1=inst.arg1, result=inst.result), f"Algebraic Simplification: '{inst.to_str()}' -> '{inst.result} = {inst.arg1}'"

            # x * 1 -> x
            if inst.op == "*":
                if inst.arg2 == "1":
                    return TACInstruction("=", arg1=inst.arg1, result=inst.result), f"Algebraic Simplification: '{inst.to_str()}' -> '{inst.result} = {inst.arg1}'"
                if inst.arg1 == "1":
                    return TACInstruction("=", arg1=inst.arg2, result=inst.result), f"Algebraic Simplification: '{inst.to_str()}' -> '{inst.result} = {inst.arg2}'"
                # x * 0 -> 0
                if inst.arg1 == "0" or inst.arg2 == "0":
                    return TACInstruction("=", arg1="0", result=inst.result), f"Algebraic Simplification: '{inst.to_str()}' -> '{inst.result} = 0'"

        # Boolean folding for 'not'
        if inst.op == "not" and inst.arg1 in ("true", "false"):
            res = "false" if inst.arg1 == "true" else "true"
            old_rep = inst.to_str()
            new_inst = TACInstruction("=", arg1=res, result=inst.result)
            return new_inst, f"Constant Folding: '{old_rep}' -> '{new_inst.to_str()}'"

        return inst, None

    def _forward_temporaries(self, instructions: List[TACInstruction]) -> Tuple[List[TACInstruction], bool]:
        """Forward simple temporary assignments e.g.:
        t0 = 30
        x = t0
        becomes:
        x = 30 (if t0 is not used elsewhere)
        """
        temp_defs: Dict[str, str] = {}
        # Count usages of each temporary
        usage_count: Dict[str, int] = {}
        for inst in instructions:
            for arg in (inst.arg1, inst.arg2):
                if arg and arg.startswith("t") and arg[1:].isdigit():
                    usage_count[arg] = usage_count.get(arg, 0) + 1

        # Check which temps can be replaced
        new_list: List[TACInstruction] = []
        changed = False

        for inst in instructions:
            arg1 = inst.arg1
            arg2 = inst.arg2

            # Replace arg1/arg2 if they are tracked single-use constants
            if arg1 in temp_defs:
                arg1 = temp_defs[arg1]
                changed = True
            if arg2 in temp_defs:
                arg2 = temp_defs[arg2]
                changed = True

            # If this is temp assignment of literal e.g. t0 = 30
            if inst.op == "=" and inst.result and inst.result.startswith("t") and inst.result[1:].isdigit():
                if usage_count.get(inst.result, 0) == 1 and (is_number(arg1) or is_string_literal(arg1) or arg1 in ("true", "false")):
                    temp_defs[inst.result] = arg1
                    self.logs.append(f"Constant Propagation: inlined temporary '{inst.result}' = {arg1}")
                    continue  # Remove the redundant temp assignment instruction

            new_list.append(TACInstruction(inst.op, arg1, arg2, inst.result, inst.comment))

        return new_list, changed
