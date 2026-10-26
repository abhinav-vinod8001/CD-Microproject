"""
Recursive-Descent Syntax Analyzer (Parser) for the Malayalam Educational Programming Language.
Produces an Abstract Syntax Tree (AST) and detailed syntax diagnostics.
"""

from typing import List, Optional
from .tokens import Token, TokenType
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


class ParserError(Exception):
    def __init__(self, message: str, line: int = 1, column: int = 1):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Syntax Error at line {line}, column {column}: {message}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # Return EOF

    def _check(self, *types: TokenType) -> bool:
        return self._peek().type in types

    def _match(self, *types: TokenType) -> Optional[Token]:
        if self._check(*types):
            tok = self._peek()
            self.pos += 1
            return tok
        return None

    def _consume(self, token_type: TokenType, error_message: str) -> Token:
        if self._check(token_type):
            tok = self._peek()
            self.pos += 1
            return tok
        curr = self._peek()
        raise ParserError(
            f"{error_message} (found '{curr.value}' [{curr.type.name}])",
            curr.line,
            curr.column,
        )

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self.pos += 1

    def parse(self) -> ProgramNode:
        statements: List[ASTNode] = []
        self._skip_newlines()

        while not self._check(TokenType.EOF):
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
            self._skip_newlines()

        return ProgramNode(statements)

    def _statement(self) -> ASTNode:
        self._skip_newlines()
        tok = self._peek()

        if tok.type == TokenType.PRINT:
            return self._print_statement()

        if tok.type == TokenType.INPUT:
            # Standalone input statement: വായിക്കുക x  or input x
            return self._input_statement()

        if tok.type == TokenType.IF:
            return self._if_statement()

        if tok.type == TokenType.WHILE:
            return self._while_statement()

        if tok.type == TokenType.IDENTIFIER:
            # Lookahead: is next '='?
            if self._peek(1).type == TokenType.ASSIGN:
                return self._assignment_statement()
            else:
                raise ParserError(
                    f"Unexpected identifier '{tok.value}'. Did you mean to assign with '=' or print with 'കാണിക്കുക'?",
                    tok.line,
                    tok.column,
                )

        raise ParserError(
            f"Unexpected statement starting with '{tok.value}' [{tok.type.name}]",
            tok.line,
            tok.column,
        )

    def _assignment_statement(self) -> AssignNode:
        ident_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        assign_tok = self._consume(TokenType.ASSIGN, "Expected '=' in assignment")

        # Check if right hand side is a standalone input call e.g. x = വായിക്കുക() or x = input()
        if self._check(TokenType.INPUT):
            self.pos += 1  # consume INPUT
            prompt: Optional[str] = None
            if self._match(TokenType.LPAREN):
                if self._check(TokenType.STRING):
                    prompt = self._consume(TokenType.STRING, "Expected prompt string").value
                self._consume(TokenType.RPAREN, "Expected ')' after input")
            expr = InputExprNode(prompt=prompt, line=ident_tok.line)
        else:
            expr = self._expression()

        # Optional delimiter or newline
        self._match(TokenType.NEWLINE)
        return AssignNode(target=ident_tok.value, expr=expr, line=ident_tok.line)

    def _print_statement(self) -> PrintNode:
        print_tok = self._consume(TokenType.PRINT, "Expected 'കാണിക്കുക' or 'print'")
        expressions: List[ASTNode] = []

        expr = self._expression()
        expressions.append(expr)

        while self._match(TokenType.COMMA):
            self._skip_newlines()
            expressions.append(self._expression())

        self._match(TokenType.NEWLINE)
        return PrintNode(expressions=expressions, line=print_tok.line)

    def _input_statement(self) -> InputNode:
        input_tok = self._consume(TokenType.INPUT, "Expected 'വായിക്കുക' or 'input'")
        prompt: Optional[str] = None

        # Check if optional string prompt follows: വായിക്കുക "സന്ദേശം", x
        if self._check(TokenType.STRING):
            prompt = self._consume(TokenType.STRING, "").value
            self._match(TokenType.COMMA)

        target_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name to store input")
        self._match(TokenType.NEWLINE)
        return InputNode(target=target_tok.value, prompt=prompt, line=input_tok.line)

    def _if_statement(self) -> IfNode:
        if_tok = self._consume(TokenType.IF, "Expected 'എങ്കിൽ' or 'if'")
        cond = self._expression()
        self._match(TokenType.NEWLINE)
        self._skip_newlines()

        then_body: List[ASTNode] = []
        while not self._check(TokenType.ELSE, TokenType.END, TokenType.EOF):
            stmt = self._statement()
            if stmt:
                then_body.append(stmt)
            self._skip_newlines()

        else_body: Optional[List[ASTNode]] = None
        if self._match(TokenType.ELSE):
            self._match(TokenType.NEWLINE)
            self._skip_newlines()
            else_body = []
            while not self._check(TokenType.END, TokenType.EOF):
                stmt = self._statement()
                if stmt:
                    else_body.append(stmt)
                self._skip_newlines()

        if not self._check(TokenType.END):
            raise ParserError(
                f"Missing closing 'അവസാനിപ്പിക്കുക' (end) for 'എങ്കിൽ' (if) block started at line {if_tok.line}",
                self._peek().line,
                self._peek().column,
            )

        self._consume(TokenType.END, "Expected 'അവസാനിപ്പിക്കുക' or 'end'")
        self._match(TokenType.NEWLINE)

        return IfNode(condition=cond, then_body=then_body, else_body=else_body, line=if_tok.line)

    def _while_statement(self) -> WhileNode:
        while_tok = self._consume(TokenType.WHILE, "Expected 'ആവർത്തിക്കുക' or 'while'")
        cond = self._expression()
        self._match(TokenType.NEWLINE)
        self._skip_newlines()

        body: List[ASTNode] = []
        while not self._check(TokenType.END, TokenType.EOF):
            stmt = self._statement()
            if stmt:
                body.append(stmt)
            self._skip_newlines()

        if not self._check(TokenType.END):
            raise ParserError(
                f"Missing closing 'അവസാനിപ്പിക്കുക' (end) for 'ആവർത്തിക്കുക' (while) loop started at line {while_tok.line}",
                self._peek().line,
                self._peek().column,
            )

        self._consume(TokenType.END, "Expected 'അവസാനിപ്പിക്കുക' or 'end'")
        self._match(TokenType.NEWLINE)

        return WhileNode(condition=cond, body=body, line=while_tok.line)

    # ---------------- Expression Parsing ----------------

    def _expression(self) -> ASTNode:
        return self._logical_or()

    def _logical_or(self) -> ASTNode:
        expr = self._logical_and()
        while self._check(TokenType.OR):
            op_tok = self._peek()
            self.pos += 1
            right = self._logical_and()
            expr = BinaryOpNode(left=expr, op="or", right=right, line=op_tok.line)
        return expr

    def _logical_and(self) -> ASTNode:
        expr = self._equality()
        while self._check(TokenType.AND):
            op_tok = self._peek()
            self.pos += 1
            right = self._equality()
            expr = BinaryOpNode(left=expr, op="and", right=right, line=op_tok.line)
        return expr

    def _equality(self) -> ASTNode:
        expr = self._relational()
        while self._check(TokenType.EQ, TokenType.NEQ):
            op_tok = self._peek()
            self.pos += 1
            right = self._relational()
            expr = BinaryOpNode(left=expr, op=op_tok.value, right=right, line=op_tok.line)
        return expr

    def _relational(self) -> ASTNode:
        expr = self._additive()
        while self._check(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op_tok = self._peek()
            self.pos += 1
            right = self._additive()
            expr = BinaryOpNode(left=expr, op=op_tok.value, right=right, line=op_tok.line)
        return expr

    def _additive(self) -> ASTNode:
        expr = self._multiplicative()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._peek()
            self.pos += 1
            right = self._multiplicative()
            expr = BinaryOpNode(left=expr, op=op_tok.value, right=right, line=op_tok.line)
        return expr

    def _multiplicative(self) -> ASTNode:
        expr = self._unary()
        while self._check(TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op_tok = self._peek()
            self.pos += 1
            right = self._unary()
            expr = BinaryOpNode(left=expr, op=op_tok.value, right=right, line=op_tok.line)
        return expr

    def _unary(self) -> ASTNode:
        if self._check(TokenType.PLUS, TokenType.MINUS, TokenType.NOT):
            op_tok = self._peek()
            self.pos += 1
            operand = self._unary()
            op_str = "not" if op_tok.type == TokenType.NOT else op_tok.value
            return UnaryOpNode(op=op_str, operand=operand, line=op_tok.line)
        return self._primary()

    def _primary(self) -> ASTNode:
        tok = self._peek()

        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return NumberNode(value=tok.value, line=tok.line)

        if tok.type == TokenType.STRING:
            self.pos += 1
            return StringNode(value=tok.value, line=tok.line)

        if tok.type == TokenType.TRUE:
            self.pos += 1
            return BooleanNode(value=True, line=tok.line)

        if tok.type == TokenType.FALSE:
            self.pos += 1
            return BooleanNode(value=False, line=tok.line)

        if tok.type == TokenType.IDENTIFIER:
            self.pos += 1
            return VariableNode(name=tok.value, line=tok.line)

        if tok.type == TokenType.INPUT:
            # Inline input expression: വായിക്കുക() or input("Enter: ")
            self.pos += 1
            prompt: Optional[str] = None
            if self._match(TokenType.LPAREN):
                if self._check(TokenType.STRING):
                    prompt = self._consume(TokenType.STRING, "Expected prompt").value
                self._consume(TokenType.RPAREN, "Expected ')' after input")
            return InputExprNode(prompt=prompt, line=tok.line)

        if tok.type == TokenType.LPAREN:
            self.pos += 1
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' to close expression")
            return expr

        raise ParserError(f"Expected expression, but found '{tok.value}' [{tok.type.name}]", tok.line, tok.column)
