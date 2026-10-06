from src.Tokens import Token, TokenType as T
from src.Parser import Parser  # Changed from src.parser to src.Parser
from src.errors import MiniLangSyntaxError
from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, Program, RealLiteral)
import unittest

def mock_tokens(*token_data):
    """Helper to generate a list of tokens with an EOF for parser unit testing."""
    tokens = [Token(t_type, lexeme, 1) for t_type, lexeme in token_data]
    tokens.append(Token(T.EOF, "", 1))
    return tokens


class TestInterpreter(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)
    
    def test_parse_declaration_int(self):
        tokens = mock_tokens((T.INT, "int"), (T.IDENTIFIER, "count"), (T.SEMICOLON, ";"))
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast, Program)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], Declaration)

    def test_parse_declaration_real(self):
        tokens = mock_tokens((T.REAL, "real"), (T.IDENTIFIER, "price"), (T.SEMICOLON, ";"))
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast.statements[0], Declaration)

    def test_parse_assignment_integer_literal(self):
        tokens = mock_tokens((T.IDENTIFIER, "x"), (T.ASSIGN, "="), (T.INTEGER_LITERAL, "42"), (T.SEMICOLON, ";"))
        parser = Parser(tokens)
        ast = parser.parse()
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertIsInstance(stmt.expression, IntegerLiteral)

    def test_parse_print_statement(self):
        tokens = mock_tokens(
            (T.PRINT, "print"), (T.LEFT_PAREN, "("), 
            (T.IDENTIFIER, "y"), 
            (T.RIGHT_PAREN, ")"), (T.SEMICOLON, ";")
        )
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast.statements[0], PrintStatement)
        self.assertIsInstance(ast.statements[0].expression, Identifier)

    def test_operator_precedence(self):
        # x = 1 + 2 * 3; 
        # (Multiplication should be deeper in the AST than addition)
        tokens = mock_tokens(
            (T.IDENTIFIER, "x"), (T.ASSIGN, "="),
            (T.INTEGER_LITERAL, "1"), (T.PLUS, "+"), 
            (T.INTEGER_LITERAL, "2"), (T.MULTIPLY, "*"), 
            (T.INTEGER_LITERAL, "3"), (T.SEMICOLON, ";")
        )
        parser = Parser(tokens)
        ast = parser.parse()
        
        assign = ast.statements[0]
        self.assertIsInstance(assign.expression, BinaryExpression)
        # The root of the expression tree should be '+'
        self.assertEqual(assign.expression.operator, "+")  # Assuming AST stores lexeme
        # The right side of the '+' should be the '*' BinaryExpression
        self.assertIsInstance(assign.expression.right, BinaryExpression)
        self.assertEqual(assign.expression.right.operator, "*")

    def test_parentheses_grouping(self):
        # x = (1 + 2) * 3;
        tokens = mock_tokens(
            (T.IDENTIFIER, "x"), (T.ASSIGN, "="),
            (T.LEFT_PAREN, "("), (T.INTEGER_LITERAL, "1"), (T.PLUS, "+"), (T.INTEGER_LITERAL, "2"), (T.RIGHT_PAREN, ")"),
            (T.MULTIPLY, "*"), (T.INTEGER_LITERAL, "3"), (T.SEMICOLON, ";")
        )
        parser = Parser(tokens)
        ast = parser.parse()
        
        assign = ast.statements[0]
        self.assertIsInstance(assign.expression, BinaryExpression)
        # The root of the expression tree should be '*'
        self.assertEqual(assign.expression.operator, "*")
        # The left side should be the '+' BinaryExpression
        self.assertIsInstance(assign.expression.left, BinaryExpression)
        self.assertEqual(assign.expression.left.operator, "+")

    # ==========================================
    # Syntax Error Tests
    # ==========================================
    def test_left_associativity(self):
        # x = 10 - 5 - 2;
        tokens = mock_tokens(
            (T.IDENTIFIER, "x"), (T.ASSIGN, "="),
            (T.INTEGER_LITERAL, "10"), (T.MINUS, "-"), 
            (T.INTEGER_LITERAL, "5"), (T.MINUS, "-"), 
            (T.INTEGER_LITERAL, "2"), (T.SEMICOLON, ";")
        )
        parser = Parser(tokens)
        ast = parser.parse()
        
        assign = ast.statements[0]
        # The root operator should be the SECOND minus sign
        self.assertIsInstance(assign.expression, BinaryExpression)
        self.assertEqual(assign.expression.operator, "-")
        # The right side should just be '2'
        self.assertIsInstance(assign.expression.right, IntegerLiteral)
        self.assertEqual(assign.expression.right.value, 2)
        # The left side should be '10 - 5'
        self.assertIsInstance(assign.expression.left, BinaryExpression)
        self.assertEqual(assign.expression.left.operator, "-")
    
    def test_missing_semicolon_on_declaration(self):
        tokens = mock_tokens((T.INT, "int"), (T.IDENTIFIER, "x"))
        parser = Parser(tokens)
        with self.assertRaises(MiniLangSyntaxError) as context:
            parser.parse()
        self.assertIn("Expected ';'", str(context.exception))

    def test_missing_semicolon_on_assignment(self):
        tokens = mock_tokens((T.IDENTIFIER, "x"), (T.ASSIGN, "="), (T.INTEGER_LITERAL, "5"))
        parser = Parser(tokens)
        with self.assertRaises(MiniLangSyntaxError) as context:
            parser.parse()
        self.assertIn("Expected ';'", str(context.exception))

    def test_missing_right_parenthesis(self):
        tokens = mock_tokens(
            (T.PRINT, "print"), (T.LEFT_PAREN, "("), 
            (T.IDENTIFIER, "y"), (T.SEMICOLON, ";")
        )
        parser = Parser(tokens)
        with self.assertRaises(MiniLangSyntaxError) as context:
            parser.parse()
        self.assertIn("Expected ')'", str(context.exception))

    def test_invalid_statement_start(self):
        # Starting a statement with a literal instead of int/real/identifier/print
        tokens = mock_tokens((T.INTEGER_LITERAL, "10"), (T.SEMICOLON, ";"))
        parser = Parser(tokens)
        with self.assertRaises(MiniLangSyntaxError) as context:
            parser.parse()
        self.assertIn("Unexpected", str(context.exception))
        self.assertIn("Expected a declaration, assignment, or print statement", str(context.exception))

    def test_missing_identifier_in_declaration(self):
        # int ;
        tokens = mock_tokens((T.INT, "int"), (T.SEMICOLON, ";"))
        parser = Parser(tokens)
        with self.assertRaises(MiniLangSyntaxError) as context:
            parser.parse()
        self.assertIn("Expected identifier", str(context.exception))

if __name__ == '__main__':
    unittest.main()
