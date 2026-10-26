"""
Malayalam Educational Programming Language Compiler Package
"""

from .tokens import Token, TokenType, MALAYALAM_KEYWORDS, ENGLISH_KEYWORDS
from .lexer import Lexer, LexerError
from .parser import Parser, ParserError
from .semantic import SemanticAnalyzer, SemanticError
from .codegen_tac import TACGenerator, TACInstruction
from .optimizer import Optimizer
from .codegen_target import TargetCodeGenerator
from .interpreter import Interpreter, InterpreterRuntimeError
from .translator import translate_code
from .pipeline import compile_and_run, inspect_pipeline

__all__ = [
    "Token",
    "TokenType",
    "MALAYALAM_KEYWORDS",
    "ENGLISH_KEYWORDS",
    "Lexer",
    "LexerError",
    "Parser",
    "ParserError",
    "SemanticAnalyzer",
    "SemanticError",
    "TACGenerator",
    "TACInstruction",
    "Optimizer",
    "TargetCodeGenerator",
    "Interpreter",
    "InterpreterRuntimeError",
    "translate_code",
    "compile_and_run",
    "inspect_pipeline",
]
