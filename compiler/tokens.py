"""
Token definitions and keyword dictionaries for the Malayalam Educational Compiler.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict


class TokenType(Enum):
    # Keywords
    PRINT = auto()       # കാണിക്കുക / print
    INPUT = auto()       # വായിക്കുക / input / read
    IF = auto()          # എങ്കിൽ / if
    ELSE = auto()        # അല്ലെങ്കിൽ / else
    WHILE = auto()       # ആവർത്തിക്കുക / while
    END = auto()         # അവസാനിപ്പിക്കുക / end
    TRUE = auto()        # ശരി / true
    FALSE = auto()       # തെറ്റ് / false
    AND = auto()         # ഒപ്പം / and
    OR = auto()          # അഥവാ / or
    NOT = auto()         # അല്ല / not

    # Literals
    NUMBER = auto()      # 10, 3.14
    STRING = auto()      # "നമസ്കാരം", "Hello"
    IDENTIFIER = auto()  # x, y, തുക, സംഖ്യ

    # Operators
    ASSIGN = auto()      # =
    PLUS = auto()        # +
    MINUS = auto()       # -
    MUL = auto()         # *
    DIV = auto()         # /
    MOD = auto()         # %

    # Comparison
    EQ = auto()          # ==
    NEQ = auto()         # !=
    LT = auto()          # <
    GT = auto()          # >
    LTE = auto()         # <=
    GTE = auto()         # >=

    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,
    NEWLINE = auto()     # \n
    EOF = auto()         # End of file


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.name,
            "value": str(self.value),
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"


# Primary keyword mappings for Malayalam
MALAYALAM_KEYWORDS: Dict[str, TokenType] = {
    "കാണിക്കുക": TokenType.PRINT,
    "വായിക്കുക": TokenType.INPUT,
    "എങ്കിൽ": TokenType.IF,
    "അല്ലെങ്കിൽ": TokenType.ELSE,
    "ആവർത്തിക്കുക": TokenType.WHILE,
    "അവസാനിപ്പിക്കുക": TokenType.END,
    "ശരി": TokenType.TRUE,
    "തെറ്റ്": TokenType.FALSE,
    "ഒപ്പം": TokenType.AND,
    "അഥവാ": TokenType.OR,
    "അല്ല": TokenType.NOT,
}

# English keyword equivalents
ENGLISH_KEYWORDS: Dict[str, TokenType] = {
    "print": TokenType.PRINT,
    "input": TokenType.INPUT,
    "read": TokenType.INPUT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "end": TokenType.END,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}

# Translation Dictionaries (1-to-1 canonical translation)
MALAYALAM_TO_ENGLISH: Dict[str, str] = {
    "കാണിക്കുക": "print",
    "വായിക്കുക": "input",
    "എങ്കിൽ": "if",
    "അല്ലെങ്കിൽ": "else",
    "ആവർത്തിക്കുക": "while",
    "അവസാനിപ്പിക്കുക": "end",
    "ശരി": "true",
    "തെറ്റ്": "false",
    "ഒപ്പം": "and",
    "അഥവാ": "or",
    "അല്ല": "not",
}

ENGLISH_TO_MALAYALAM: Dict[str, str] = {
    "print": "കാണിക്കുക",
    "input": "വായിക്കുക",
    "read": "വായിക്കുക",
    "if": "എങ്കിൽ",
    "else": "അല്ലെങ്കിൽ",
    "while": "ആവർത്തിക്കുക",
    "end": "അവസാനിപ്പിക്കുക",
    "true": "ശരി",
    "false": "തെറ്റ്",
    "and": "ഒപ്പം",
    "or": "അഥവാ",
    "not": "അല്ല",
}
