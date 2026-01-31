"""
Parser module for Jack language syntax analysis.

This module provides the Parser class that parses tokenized Jack source code
and generates an XML parse tree according to the Jack grammar.
"""

from typing import List, TextIO


# Statement keywords for checking statement types
STATEMENT_KEYWORDS: List[str] = [
    '<keyword> if </keyword>\n',
    '<keyword> let </keyword>\n',
    '<keyword> while </keyword>\n',
    '<keyword> do </keyword>\n',
    '<keyword> return </keyword>\n'
]

# Operator symbols for expression parsing
OPERATOR_SYMBOLS: List[str] = [
    '<symbol> + </symbol>\n',
    '<symbol> - </symbol>\n',
    '<symbol> * </symbol>\n',
    '<symbol> / </symbol>\n',
    '<symbol> &amp; </symbol>\n',
    '<symbol> | </symbol>\n',
    '<symbol> &lt; </symbol>\n',
    '<symbol> &gt; </symbol>\n',
    '<symbol> = </symbol>\n'
]

# Keyword constants for term parsing
KEYWORD_CONSTANTS: List[str] = [
    '<keyword> true </keyword>\n',
    '<keyword> false </keyword>\n',
    '<keyword> null </keyword>\n',
    '<keyword> this </keyword>\n'
]


class Parser:
    """
    Parser for Jack language that generates XML parse tree from tokens.

    Reads tokenized XML input and produces a structured XML parse tree
    following the Jack grammar specification.
    """

    def __init__(self, input_file: str, output_file: str) -> None:
        """
        Initialize the parser and start compilation.

        Args:
            input_file: Path to the tokenized XML input file.
            output_file: Path for the output parse tree XML file.
        """
        self.tokens: List[str] = []
        self.token_counter: int = 0
        self.indent_level: int = 0

        # Read tokens from input file
        tokens_raw: List[str] = []
        with open(input_file) as f:
            for line in f:
                tokens_raw.append(line)

        # Remove <tokens> wrapper tags
        self.tokens = tokens_raw[1:-1]
        self.output: TextIO = open(output_file, 'w')
        self.current_token: str = self.tokens[self.token_counter]

        # Start compilation
        self._compile_class()
        self.output.close()

    def _compile_class(self) -> None:
        """Compile a complete class definition."""
        self.output.write('<class>\n')
        self._increase_indent()
        self._write_and_advance()  # 'class'
        self._write_and_advance()  # className
        self._write_and_advance()  # '{'

        self._compile_class_var_dec()
        self._compile_subroutine()

        self._write_indent()
        self.output.write(self.current_token)  # '}'
        self.output.write('</class>\n')

    def _compile_class_var_dec(self) -> None:
        """Compile class variable declarations (field/static)."""
        if self.current_token in ('<keyword> field </keyword>\n',
                                   '<keyword> static </keyword>\n'):
            self._write_indent()
            self.output.write('<classVarDec>\n')
            self._increase_indent()

            # Process until semicolon
            while self.current_token != '<symbol> ; </symbol>\n':
                self._write_and_advance()
            self._write_and_advance()  # ';'

            self._decrease_indent()
            self._write_indent()
            self.output.write('</classVarDec>\n')

        # Recursively check for more declarations
        if self.current_token in ('<keyword> field </keyword>\n',
                                   '<keyword> static </keyword>\n'):
            self._compile_class_var_dec()

    def _compile_subroutine(self) -> None:
        """Compile a subroutine declaration (constructor/function/method)."""
        self._write_indent()
        self.output.write('<subroutineDec>\n')
        self._increase_indent()

        self._write_and_advance()  # constructor|function|method
        self._write_and_advance()  # void|type
        self._write_and_advance()  # subroutineName
        self._write_and_advance()  # '('

        self._compile_parameter_list()
        self._write_and_advance()  # ')'

        self._write_indent()
        self.output.write('<subroutineBody>\n')
        self._increase_indent()
        self._write_and_advance()  # '{'

        # Compile variable declarations
        if self.current_token == '<keyword> var </keyword>\n':
            self._compile_var_dec()

        self._compile_statements()
        self._write_and_advance()  # '}'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineBody>\n')
        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineDec>\n')

        # Check for more subroutines
        if self.current_token in ('<keyword> constructor </keyword>\n',
                                   '<keyword> function </keyword>\n',
                                   '<keyword> method </keyword>\n'):
            self._compile_subroutine()

    def _compile_parameter_list(self) -> None:
        """Compile a parameter list for a subroutine."""
        self._write_indent()
        self.output.write('<parameterList>\n')
        self._increase_indent()

        while self.current_token != '<symbol> ) </symbol>\n':
            self._write_and_advance()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</parameterList>\n')

    def _compile_var_dec(self) -> None:
        """Compile a local variable declaration."""
        self._write_indent()
        self.output.write('<varDec>\n')
        self._increase_indent()

        while self.current_token != '<symbol> ; </symbol>\n':
            self._write_and_advance()

        self._write_and_advance()  # ';'
        self._decrease_indent()
        self._write_indent()
        self.output.write('</varDec>\n')

        # Recursively check for more var declarations
        if self.current_token == '<keyword> var </keyword>\n':
            self._compile_var_dec()

    def _compile_statements(self) -> None:
        """Compile a sequence of statements."""
        self._write_indent()
        self.output.write('<statements>\n')
        self._increase_indent()

        while self._is_statement():
            if self.current_token == '<keyword> if </keyword>\n':
                self._compile_if()
            elif self.current_token == '<keyword> let </keyword>\n':
                self._compile_let()
            elif self.current_token == '<keyword> while </keyword>\n':
                self._compile_while()
            elif self.current_token == '<keyword> do </keyword>\n':
                self._compile_do()
            elif self.current_token == '<keyword> return </keyword>\n':
                self._compile_return()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</statements>\n')

    def _compile_do(self) -> None:
        """Compile a do statement (subroutine call)."""
        self._write_indent()
        self.output.write('<doStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'do'

        # LL(2) lookahead for subroutine call type
        lookahead = self.tokens[self.token_counter + 1]
        if lookahead == '<symbol> ( </symbol>\n':
            self._write_and_advance()  # subroutineName
            self._write_and_advance()  # '('
            self._compile_expression_list()
            self._write_and_advance()  # ')'
            self._write_and_advance()  # ';'
        else:
            self._write_and_advance()  # className|varName
            self._write_and_advance()  # '.'
            self._write_and_advance()  # subroutineName
            self._write_and_advance()  # '('
            self._compile_expression_list()
            self._write_and_advance()  # ')'
            self._write_and_advance()  # ';'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</doStatement>\n')

    def _compile_let(self) -> None:
        """Compile a let statement (variable assignment)."""
        self._write_indent()
        self.output.write('<letStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'let'
        self._write_and_advance()  # varName

        # Check for array indexing
        if self.current_token == '<symbol> [ </symbol>\n':
            self._write_and_advance()  # '['
            self._compile_expression()
            self._write_and_advance()  # ']'

        self._write_and_advance()  # '='
        self._compile_expression()
        self._write_and_advance()  # ';'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</letStatement>\n')

    def _compile_while(self) -> None:
        """Compile a while statement."""
        self._write_indent()
        self.output.write('<whileStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'while'
        self._write_and_advance()  # '('
        self._compile_expression()
        self._write_and_advance()  # ')'
        self._write_and_advance()  # '{'
        self._compile_statements()
        self._write_and_advance()  # '}'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</whileStatement>\n')

    def _compile_return(self) -> None:
        """Compile a return statement."""
        self._write_indent()
        self.output.write('<returnStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'return'

        # Check for return expression
        if self._has_more_terms():
            self._compile_expression()
        self._write_and_advance()  # ';'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</returnStatement>\n')

    def _compile_if(self) -> None:
        """Compile an if statement with optional else clause."""
        self._write_indent()
        self.output.write('<ifStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'if'
        self._write_and_advance()  # '('
        self._compile_expression()
        self._write_and_advance()  # ')'
        self._write_and_advance()  # '{'
        self._compile_statements()
        self._write_and_advance()  # '}'

        # Check for else clause
        if self.current_token == '<keyword> else </keyword>\n':
            self._write_and_advance()  # 'else'
            self._write_and_advance()  # '{'
            self._compile_statements()
            self._write_and_advance()  # '}'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</ifStatement>\n')

    def _compile_expression(self) -> None:
        """Compile an expression (term (op term)*)."""
        self._write_indent()
        self.output.write('<expression>\n')
        self._increase_indent()

        self._compile_term()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</expression>\n')

    def _compile_term(self) -> None:
        """Compile a term in an expression."""
        self._write_indent()
        self.output.write('<term>\n')
        self._increase_indent()

        token_type = self.current_token.split()[0]

        if token_type == '<identifier>':
            lookahead = self.tokens[self.token_counter + 1]
            if lookahead == '<symbol> [ </symbol>\n':
                self._write_and_advance()  # varName
                self._write_and_advance()  # '['
                self._compile_expression()
                self._write_and_advance()  # ']'
            elif lookahead == '<symbol> ( </symbol>\n':
                self._write_and_advance()  # subroutineName
                self._write_and_advance()  # '('
                self._compile_expression_list()
                self._write_and_advance()  # ')'
            elif lookahead == '<symbol> . </symbol>\n':
                self._write_and_advance()  # className|varName
                self._write_and_advance()  # '.'
                self._write_and_advance()  # subroutineName
                self._write_and_advance()  # '('
                self._compile_expression_list()
                self._write_and_advance()  # ')'
            else:
                self._write_and_advance()  # varName
        elif token_type == '<integerConstant>':
            self._write_and_advance()
        elif token_type == '<stringConstant>':
            self._write_and_advance()
        elif self.current_token in KEYWORD_CONSTANTS:
            self._write_and_advance()
        elif self.current_token == '<symbol> ( </symbol>\n':
            self._write_and_advance()  # '('
            self._compile_expression()
            self._write_and_advance()  # ')'
        elif self.current_token in ('<symbol> - </symbol>\n',
                                     '<symbol> ~ </symbol>\n'):
            self._write_and_advance()  # unary operator
            self._compile_term()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</term>\n')

        # Check for operator and additional terms
        if self._is_operator():
            self._write_and_advance()  # operator
            self._compile_term()

    def _compile_expression_list(self) -> None:
        """Compile a comma-separated list of expressions."""
        self._write_indent()
        self.output.write('<expressionList>\n')
        self._increase_indent()

        while self._has_more_terms():
            self._compile_expression()
            if self.current_token == '<symbol> , </symbol>\n':
                self._write_and_advance()  # ','

        self._decrease_indent()
        self._write_indent()
        self.output.write('</expressionList>\n')

    def _write_indent(self) -> None:
        """Write indentation to output based on current indent level."""
        self.output.write('  ' * self.indent_level)

    def _advance(self) -> None:
        """Advance to the next token."""
        self.token_counter += 1
        self.current_token = self.tokens[self.token_counter]

    def _write_and_advance(self) -> None:
        """Write current token with indentation and advance to next."""
        self._write_indent()
        self.output.write(self.current_token)
        self._advance()

    def _increase_indent(self) -> None:
        """Increase indentation level."""
        self.indent_level += 1

    def _decrease_indent(self) -> None:
        """Decrease indentation level."""
        self.indent_level -= 1

    def _is_statement(self) -> bool:
        """Check if current token is a statement keyword."""
        return self.current_token in STATEMENT_KEYWORDS

    def _is_operator(self) -> bool:
        """Check if current token is an operator."""
        return self.current_token in OPERATOR_SYMBOLS

    def _has_more_terms(self) -> bool:
        """Check if current token can start a term."""
        token_type = self.current_token.split()[0]

        if token_type == '<identifier>':
            return True
        if token_type in ('<integerConstant>', '<stringConstant>'):
            return True
        if self.current_token in KEYWORD_CONSTANTS:
            return True
        if self.current_token == '<symbol> ( </symbol>\n':
            return True
        if self.current_token in ('<symbol> - </symbol>\n',
                                   '<symbol> ~ </symbol>\n'):
            return True
        return False

