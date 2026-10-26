"""
Compiler Pipeline Orchestrator for the Malayalam Educational Programming Language.
Connects all 8 compiler stages sequentially and provides deep inspection data for each stage.
"""

from typing import Dict, Any, List, Optional
import time

from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .semantic import SemanticAnalyzer, SemanticError
from .codegen_tac import TACGenerator
from .optimizer import Optimizer
from .codegen_target import TargetCodeGenerator
from .interpreter import Interpreter, InterpreterRuntimeError, InputRequiredException


def format_tokens_table(tokens) -> str:
    lines = [f"{'#':<4} {'TOKEN TYPE':<16} {'LEXEME / VALUE':<24} {'LINE:COL':<10}"]
    lines.append("-" * 58)
    for i, t in enumerate(tokens, 1):
        val_str = repr(t.value) if isinstance(t.value, str) else str(t.value)
        lines.append(f"{i:<4} {t.type.name:<16} {val_str:<24} L{t.line}:C{t.column}")
    return "\n".join(lines)


def format_tac_listing(instructions) -> str:
    lines = []
    for i, inst in enumerate(instructions, 1):
        cmt = f"  ; {inst.comment}" if inst.comment else ""
        lines.append(f"{i:03d}:  {inst.to_str():<28}{cmt}")
    return "\n".join(lines)


def inspect_pipeline(source_code: str, inputs: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Runs all 8 compiler pipeline stages step-by-step and collects
    rich inspection data from each stage.
    """
    start_time = time.perf_counter()
    result: Dict[str, Any] = {
        "success": False,
        "needs_input": False,
        "input_request": None,
        "error": None,
        "error_stage": None,
        "execution_time_ms": 0.0,
        "stages": {},
    }

    try:
        # -------------------------------------------------------------
        # Stage 1: Lexical Analysis & Token Generation
        # -------------------------------------------------------------
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        result["stages"]["stage_1_tokens"] = {
            "title": "Stage 1: Lexical Analysis (Tokens)",
            "count": len(tokens),
            "tokens": [t.to_dict() for t in tokens],
            "text": format_tokens_table(tokens),
        }

        # -------------------------------------------------------------
        # Stage 2 & 3: Syntax Analysis, Parse Tree & AST Generation
        # -------------------------------------------------------------
        parser = Parser(tokens)
        ast = parser.parse()
        ast_dict = ast.to_dict()
        ast_tree_str = ast.to_str_tree()

        result["stages"]["stage_2_parse_tree"] = {
            "title": "Stage 2: Syntax Analysis (Parse Derivations)",
            "statement_count": len(ast.statements),
            "text": ast_tree_str,
        }

        result["stages"]["stage_3_ast"] = {
            "title": "Stage 3: Abstract Syntax Tree (AST)",
            "ast_dict": ast_dict,
            "text": ast_tree_str,
        }

        # -------------------------------------------------------------
        # Stage 4: Basic Semantic Analysis & Symbol Table
        # -------------------------------------------------------------
        semantic_analyzer = SemanticAnalyzer()
        semantic_info = semantic_analyzer.analyze(ast)

        # Format symbol table text
        sym_lines = [f"{'IDENTIFIER':<16} {'INFERRED TYPE':<15} {'SCOPE':<10} {'DEFINED LINE':<14} {'REFS'}"]
        sym_lines.append("-" * 65)
        for s in semantic_info["symbol_table"]:
            refs_str = ", ".join(f"L{r}" for r in s["references"]) or "none"
            sym_lines.append(f"{s['name']:<16} {s['type']:<15} {s['scope']:<10} L{s['line_defined']:<13} {refs_str}")

        result["stages"]["stage_4_semantic"] = {
            "title": "Stage 4: Semantic Analysis & Symbol Table",
            "symbol_table": semantic_info["symbol_table"],
            "diagnostics": semantic_info["diagnostics"],
            "text": "\n".join(sym_lines) if semantic_info["symbol_table"] else "(No symbols declared)",
        }

        # -------------------------------------------------------------
        # Stage 5: Three-Address Code (TAC) Intermediate Representation
        # -------------------------------------------------------------
        tac_gen = TACGenerator()
        tac_instructions = tac_gen.generate(ast)

        result["stages"]["stage_5_tac"] = {
            "title": "Stage 5: Three-Address Code (TAC IR)",
            "count": len(tac_instructions),
            "instructions": [inst.to_dict() for inst in tac_instructions],
            "text": format_tac_listing(tac_instructions),
        }

        # -------------------------------------------------------------
        # Stage 6: Code Optimization (Constant Folding & Propagation)
        # -------------------------------------------------------------
        optimizer = Optimizer()
        optimized_tac, opt_logs = optimizer.optimize(tac_instructions)

        result["stages"]["stage_6_optimized"] = {
            "title": "Stage 6: Code Optimization",
            "original_count": len(tac_instructions),
            "optimized_count": len(optimized_tac),
            "instructions": [inst.to_dict() for inst in optimized_tac],
            "text": format_tac_listing(optimized_tac),
            "optimization_logs": opt_logs,
        }

        # -------------------------------------------------------------
        # Stage 7: Target Code Generation (RISC/MIPS Assembly)
        # -------------------------------------------------------------
        target_gen = TargetCodeGenerator()
        target_assembly = target_gen.generate(optimized_tac)

        result["stages"]["stage_7_target_code"] = {
            "title": "Stage 7: Target Code Generation (Assembly)",
            "text": target_assembly,
        }

        # -------------------------------------------------------------
        # Stage 8: Execution using Custom Interpreter
        # -------------------------------------------------------------
        interpreter = Interpreter()
        exec_result = interpreter.execute(ast, inputs=inputs or [])

        result["stages"]["stage_8_execution"] = {
            "title": "Stage 8: Execution (Custom VM / Interpreter)",
            "output": exec_result["output"],
            "output_lines": exec_result["output_lines"],
            "environment": exec_result["environment"],
            "steps": exec_result["steps"],
            "trace": exec_result["trace"],
        }

        result["success"] = True

    except InputRequiredException as e:
        result["success"] = True
        result["needs_input"] = True
        result["input_request"] = {
            "target": e.target,
            "prompt": e.prompt,
            "line": e.line,
        }
        result["stages"]["stage_8_execution"] = {
            "title": "Stage 8: Execution (Waiting for User Input)",
            "output": "\n".join(interpreter.output),
            "output_lines": list(interpreter.output),
            "environment": dict(interpreter.environment),
            "steps": interpreter.steps,
            "trace": list(interpreter.trace),
        }
    except LexerError as e:
        result["error"] = e.message
        result["error_stage"] = "Stage 1: Lexical Analysis"
        result["line"] = e.line
        result["column"] = e.column
    except ParserError as e:
        result["error"] = e.message
        result["error_stage"] = "Stage 2: Syntax Analysis"
        result["line"] = e.line
        result["column"] = e.column
    except SemanticError as e:
        result["error"] = e.message
        result["error_stage"] = "Stage 4: Semantic Analysis"
        result["line"] = e.line
        result["column"] = 1
    except InterpreterRuntimeError as e:
        result["error"] = e.message
        result["error_stage"] = "Stage 8: Runtime Execution"
        result["line"] = e.line
        result["column"] = 1
    except Exception as e:
        result["error"] = str(e)
        result["error_stage"] = "Internal Error"

    elapsed = (time.perf_counter() - start_time) * 1000.0
    result["execution_time_ms"] = round(elapsed, 2)
    return result


def compile_and_run(source_code: str, inputs: Optional[List[str]] = None) -> Dict[str, Any]:
    """Helper shortcut to compile and run code, returning output and pipeline data."""
    return inspect_pipeline(source_code, inputs)
