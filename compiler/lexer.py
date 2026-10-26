"""
Lexical Analyzer for Malayalam Educational Programming Language.
Supports full Malayalam Unicode script and English keywords.
"""

import re
from typing import List, Optional
from .tokens import (
    Token,
    TokenType,
    MALAYALAM_KEYWORDS,
    ENGLISH_KEYWORDS,
)


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexical Error at line {line}, column {column}: {message}")


class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.length = len(source_code)
        self.pos = 0
        self.line = 1
        self.column = 1

    def _peek(self, offset: int = 0) -> Optional[str]:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return None

    def _advance(self) -> Optional[str]:
        if self.pos >= self.length:
            return None
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _is_ident_start(self, ch: str) -> bool:
        if ch is None:
            return False
        # ASCII letters, underscore, or Malayalam script block \u0D00-\u0D7F
        return bool(re.match(r'^[a-zA-Z_\u0D00-\u0D7F]$', ch))

    def _is_ident_part(self, ch: str) -> bool:
        if ch is None:
            return False
        # Letters, digits, underscores, Malayalam block, and ZWNJ/ZWJ
        return bool(re.match(r'^[a-zA-Z0-9_\u0D00-\u0D7F\u200C\u200D]$', ch))

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            ch = self._peek()

            # Skip spaces and tabs
            if ch in (' ', '\t', '\r'):
                self._advance()
                continue

            # Comments (# or //)
            if ch == '#' or (ch == '/' and self._peek(1) == '/'):
                while self._peek() is not None and self._peek() != '\n':
                    self._advance()
                continue

            # Newlines
            if ch == '\n':
                start_col = self.column
                start_line = self.line
                self._advance()
                # Condense consecutive newlines, don't add leading newlines
                if tokens and tokens[-1].type != TokenType.NEWLINE:
                    tokens.append(Token(TokenType.NEWLINE, "\\n", start_line, start_col))
                continue

            # Semicolon as newline/statement delimiter
            if ch == ';':
                start_col = self.column
                start_line = self.line
                self._advance()
                if tokens and tokens[-1].type != TokenType.NEWLINE:
                    tokens.append(Token(TokenType.NEWLINE, ";", start_line, start_col))
                continue

            # String literals
            if ch in ('"', "'"):
                quote_char = ch
                start_col = self.column
                start_line = self.line
                self._advance()  # Skip opening quote
                str_chars = []
                closed = False

                while self._peek() is not None:
                    curr = self._peek()
                    if curr == quote_char:
                        self._advance()
                        closed = True
                        break
                    elif curr == '\\':
                        self._advance()
                        escaped = self._advance()
                        if escaped == 'n':
                            str_chars.append('\n')
                        elif escaped == 't':
                            str_chars.append('\t')
                        elif escaped == '\\':
                            str_chars.append('\\')
                        elif escaped in ('"', "'"):
                            str_chars.append(escaped)
                        else:
                            str_chars.append('\\' + (escaped or ''))
                    elif curr == '\n':
                        raise LexerError("Newline found inside unclosed string literal", start_line, start_col)
                    else:
                        str_chars.append(self._advance())

                if not closed:
                    raise LexerError(f"Unclosed string literal starting at line {start_line}, column {start_col}", start_line, start_col)

                tokens.append(Token(TokenType.STRING, "".join(str_chars), start_line, start_col))
                continue

            # Numbers (integers and floats)
            if ch.isdigit():
                start_col = self.column
                start_line = self.line
                num_chars = []
                is_float = False

                while self._peek() is not None and self._peek().isdigit():
                    num_chars.append(self._advance())

                if self._peek() == '.' and self._peek(1) is not None and self._peek(1).isdigit():
                    is_float = True
                    num_chars.append(self._advance())  # add '.'
                    while self._peek() is not None and self._peek().isdigit():
                        num_chars.append(self._advance())

                num_str = "".join(num_chars)
                num_val = float(num_str) if is_float else int(num_str)
                tokens.append(Token(TokenType.NUMBER, num_val, start_line, start_col))
                continue

            # Identifiers and keywords (Malayalam and English)
            if self._is_ident_start(ch):
                start_col = self.column
                start_line = self.line
                word_chars = []

                while self._peek() is not None and self._is_ident_part(self._peek()):
                    word_chars.append(self._advance())

                word = "".join(word_chars)

                # Check keyword match
                if word in MALAYALAM_KEYWORDS:
                    ttype = MALAYALAM_KEYWORDS[word]
                    tokens.append(Token(ttype, word, start_line, start_col))
                elif word.lower() in ENGLISH_KEYWORDS:
                    ttype = ENGLISH_KEYWORDS[word.lower()]
                    tokens.append(Token(ttype, word, start_line, start_col))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, word, start_line, start_col))
                continue

            # Multi-character operators
            start_col = self.column
            start_line = self.line

            if ch == '=' and self._peek(1) == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.EQ, "==", start_line, start_col))
                continue

            if ch == '!' and self._peek(1) == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.NEQ, "!=", start_line, start_col))
                continue

            if ch == '<' and self._peek(1) == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.LTE, "<=", start_line, start_col))
                continue

            if ch == '>' and self._peek(1) == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.GTE, ">=", start_line, start_col))
                continue

            # Single-character tokens
            single_tokens = {
                '=': TokenType.ASSIGN,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MUL,
                '/': TokenType.DIV,
                '%': TokenType.MOD,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ',': TokenType.COMMA,
            }

            if ch in single_tokens:
                self._advance()
                tokens.append(Token(single_tokens[ch], ch, start_line, start_col))
                continue

            # If we reach here, it's an unrecognized character
            bad_char = self._advance()
            raise LexerError(f"Unexpected character '{bad_char}' (Unicode U+{ord(bad_char):04X})", start_line, start_col)

        # Remove trailing newline tokens
        while tokens and tokens[-1].type == TokenType.NEWLINE:
            tokens.pop()

        # Append EOF token
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens
