import unittest
import sys
import os

# Add the parent directory (project root) to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.calculator import Lexer, Token, TokenType, Parser, Interpreter

class TestCalculator(unittest.TestCase):

    def test_addition(self):
        lexer = Lexer("3+5")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 8)

    def test_subtraction(self):
        lexer = Lexer("10-4")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 6)

    def test_multiplication(self):
        lexer = Lexer("3*5")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 15)

    def test_division(self):
        lexer = Lexer("10/2")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 5)

    def test_complex_expression(self):
        lexer = Lexer("2 + 3 * 4 - 6 / 2")  # Expected: 2 + 12 - 3 = 11
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 11)

    def test_parentheses(self):
        lexer = Lexer("(2 + 3) * 4")  # Expected: 5 * 4 = 20
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 20)

    def test_unary_minus(self):
        lexer = Lexer("-3 + 5")  # Expected: 2
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 2)

    def test_unary_plus(self):
        lexer = Lexer("+3 - 5")  # Expected: -2
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, -2)

    def test_multiple_unary(self):
        lexer = Lexer("--3")  # Expected: 3
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 3)

    def test_complex_unary(self):
        lexer = Lexer("5 - -2")  # Expected: 7
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 7)

    def test_whitespace(self):
        lexer = Lexer("  3  +   5  ")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        self.assertEqual(result, 8)

    def test_no_input(self):
        lexer = Lexer("")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        with self.assertRaises(Exception):
            interpreter.interpret()

    def test_invalid_token(self):
        lexer = Lexer("3 $ 5")
        parser = Parser(lexer)
        with self.assertRaises(Exception):
            interpreter = Interpreter(parser)
            interpreter.interpret()

    def test_unexpected_eof(self):
        lexer = Lexer("3 +")
        parser = Parser(lexer)
        with self.assertRaises(Exception):
            interpreter = Interpreter(parser)
            interpreter.interpret()

    def test_division_by_zero(self):
        lexer = Lexer("10 / 0")
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        with self.assertRaises(ZeroDivisionError):
            interpreter.interpret()

if __name__ == '__main__':
    unittest.main()
