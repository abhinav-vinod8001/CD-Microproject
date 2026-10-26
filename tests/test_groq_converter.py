"""
Unit tests for Groq and offline educational multi-language converter.
"""

import unittest
from compiler.groq_converter import convert_code_multilang, offline_transpile, extract_malayalam_identifiers


class TestGroqConverter(unittest.TestCase):
    def test_extract_identifiers(self):
        code = """# Comment with മലയാളം
സംഖ്യ = 10
തുക = സംഖ്യ + 5
കാണിക്കുക തുക
"""
        idents = extract_malayalam_identifiers(code)
        self.assertIn("സംഖ്യ", idents)
        self.assertIn("തുക", idents)
        self.assertNotIn("കാണിക്കുക", idents)

    def test_offline_transpilation_python_c_java(self):
        code = """വായിക്കുക സംഖ്യ
തുക = 0
ആവർത്തിക്കുക സംഖ്യ > 0
    തുക = തുക + സംഖ്യ
    സംഖ്യ = സംഖ്യ - 1
അവസാനിപ്പിക്കുക
കാണിക്കുക തുക
"""
        res = convert_code_multilang(code)
        self.assertTrue(res["success"])
        self.assertIn("python", res)
        self.assertIn("java", res)
        self.assertIn("c", res)
        self.assertIn("dictionary", res)
        self.assertIn("educational_notes", res)

        # Check Python output
        py_code = res["python"]
        self.assertIn("while", py_code)
        self.assertIn("sum", py_code)
        self.assertIn("num", py_code)

        # Check C output
        c_code = res["c"]
        self.assertIn("#include <stdio.h>", c_code)
        self.assertIn("int main()", c_code)
        self.assertIn("scanf", c_code)

        # Check Java output
        java_code = res["java"]
        self.assertIn("public class Main", java_code)
        self.assertIn("Scanner", java_code)

        # Check Dictionary
        dict_items = {d["original"]: d["translated"] for d in res["dictionary"]}
        self.assertIn("സംഖ്യ", dict_items)
        self.assertIn("തുക", dict_items)
        self.assertIn("കാണിക്കുക", dict_items)


if __name__ == '__main__':
    unittest.main()
