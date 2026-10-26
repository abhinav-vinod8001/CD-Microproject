"""
Comprehensive Unit Tests for Malayalam Educational Compiler Pipeline.
Tests Lexer, Parser, AST, Semantic Analyzer, TAC, Optimizer, Target Code,
Interpreter, and Bidirectional Malayalam <-> English Translation.
"""

import unittest
from compiler.lexer import Lexer, LexerError
from compiler.parser import Parser, ParserError
from compiler.semantic import SemanticAnalyzer, SemanticError
from compiler.codegen_tac import TACGenerator
from compiler.optimizer import Optimizer
from compiler.codegen_target import TargetCodeGenerator
from compiler.interpreter import Interpreter, InterpreterRuntimeError
from compiler.translator import translate_code
from compiler.pipeline import inspect_pipeline, compile_and_run
from compiler.tokens import TokenType


class TestMalayalamCompiler(unittest.TestCase):

    def test_lexer_tokens(self):
        code = 'x = 10\nകാണിക്കുക "ഹലോ", x'
        tokens = Lexer(code).tokenize()
        types = [t.type for t in tokens]
        self.assertIn(TokenType.PRINT, types)
        self.assertIn(TokenType.STRING, types)
        self.assertIn(TokenType.NUMBER, types)
        self.assertIn(TokenType.IDENTIFIER, types)

    def test_lexer_unclosed_string(self):
        with self.assertRaises(LexerError):
            Lexer('s = "unclosed').tokenize()

    def test_parser_arithmetic_assignment(self):
        code = """
        x = 10
        y = 20
        z = x + y
        കാണിക്കുക z
        """
        ast = Parser(Lexer(code).tokenize()).parse()
        self.assertEqual(len(ast.statements), 4)

    def test_parser_if_else(self):
        code = """
        x = 5
        എങ്കിൽ x > 0
            കാണിക്കുക "Positive"
        അല്ലെങ്കിൽ
            കാണിക്കുക "Zero or Negative"
        അവസാനിപ്പിക്കുക
        """
        ast = Parser(Lexer(code).tokenize()).parse()
        self.assertEqual(len(ast.statements), 2)

    def test_parser_missing_end_error(self):
        code = """
        എങ്കിൽ 1 > 0
            കാണിക്കുക 1
        """
        with self.assertRaises(ParserError):
            Parser(Lexer(code).tokenize()).parse()

    def test_semantic_analysis_undeclared_var(self):
        code = "കാണിക്കുക a + 1"
        ast = Parser(Lexer(code).tokenize()).parse()
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_semantic_analysis_div_zero(self):
        code = "x = 10 / 0"
        ast = Parser(Lexer(code).tokenize()).parse()
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_tac_generation(self):
        code = "a = 10\nb = a + 5\nകാണിക്കുക b"
        ast = Parser(Lexer(code).tokenize()).parse()
        tac = TACGenerator().generate(ast)
        tac_strs = [inst.to_str() for inst in tac]
        self.assertTrue(any("print" in s for s in tac_strs))
        self.assertTrue(any("=" in s for s in tac_strs))

    def test_optimizer_constant_folding(self):
        code = "a = 10 + 20\nകാണിക്കുക a"
        ast = Parser(Lexer(code).tokenize()).parse()
        tac = TACGenerator().generate(ast)
        opt_tac, logs = Optimizer().optimize(tac)
        # Constant folding should simplify 10 + 20 to 30
        self.assertTrue(any("30" in inst.to_str() for inst in opt_tac))
        self.assertTrue(len(logs) > 0)

    def test_target_code_generation(self):
        code = "x = 42\nകാണിക്കുക x"
        ast = Parser(Lexer(code).tokenize()).parse()
        tac = TACGenerator().generate(ast)
        asm = TargetCodeGenerator().generate(tac)
        self.assertIn(".data", asm)
        self.assertIn(".text", asm)
        self.assertIn("main:", asm)
        self.assertIn("HALT", asm)

    def test_interpreter_execution(self):
        code = """
        x = 10
        y = 20
        z = x + y
        കാണിക്കുക z
        """
        res = compile_and_run(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["stages"]["stage_8_execution"]["output"].strip(), "30")
        self.assertEqual(res["stages"]["stage_8_execution"]["environment"]["z"], 30)

    def test_interpreter_while_loop(self):
        code = """
        i = 1
        sum = 0
        ആവർത്തിക്കുക i <= 4
            sum = sum + i
            i = i + 1
        അവസാനിപ്പിക്കുക
        കാണിക്കുക sum
        """
        res = compile_and_run(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["stages"]["stage_8_execution"]["output"].strip(), "10")

    def test_translation_bidirectional(self):
        malayalam_code = """
        x = 10
        എങ്കിൽ x > 5
            കാണിക്കുക "വലുത്"
        അവസാനിപ്പിക്കുക
        """
        english_code = translate_code(malayalam_code, "to_english")
        self.assertIn("if", english_code)
        self.assertIn("print", english_code)
        self.assertIn("end", english_code)
        self.assertIn('"വലുത്"', english_code)  # Preserved Malayalam string

        back_to_malayalam = translate_code(english_code, "to_malayalam")
        self.assertIn("എങ്കിൽ", back_to_malayalam)
        self.assertIn("കാണിക്കുക", back_to_malayalam)
        self.assertIn("അവസാനിപ്പിക്കുക", back_to_malayalam)

    def test_english_execution_parity(self):
        # Programs written with translated English keywords must execute with exact same result
        code_eng = """
        x = 10
        y = 20
        z = x + y
        print z
        """
        res = compile_and_run(code_eng)
        self.assertTrue(res["success"])
        self.assertEqual(res["stages"]["stage_8_execution"]["output"].strip(), "30")


if __name__ == "__main__":
    unittest.main()
