"""
Jack Parser - Recursive descent parser for Jack programming language.

Parses tokenized Jack source code and produces XML parse tree.
Part of the Nand2Tetris course (Project 10).
"""

from typing import List


class Parser:
    """Recursive descent parser for Jack language."""

    # Token constants for readability
    FIELD_TOKEN = '<keyword> field </keyword>\n'
    STATIC_TOKEN = '<keyword> static </keyword>\n'
    VAR_TOKEN = '<keyword> var </keyword>\n'
    CONSTRUCTOR_TOKEN = '<keyword> constructor </keyword>\n'
    FUNCTION_TOKEN = '<keyword> function </keyword>\n'
    METHOD_TOKEN = '<keyword> method </keyword>\n'
    IF_TOKEN = '<keyword> if </keyword>\n'
    LET_TOKEN = '<keyword> let </keyword>\n'
    WHILE_TOKEN = '<keyword> while </keyword>\n'
    DO_TOKEN = '<keyword> do </keyword>\n'
    RETURN_TOKEN = '<keyword> return </keyword>\n'
    ELSE_TOKEN = '<keyword> else </keyword>\n'
    TRUE_TOKEN = '<keyword> true </keyword>\n'
    FALSE_TOKEN = '<keyword> false </keyword>\n'
    NULL_TOKEN = '<keyword> null </keyword>\n'
    THIS_TOKEN = '<keyword> this </keyword>\n'
    LPAREN_TOKEN = '<symbol> ( </symbol>\n'
    RPAREN_TOKEN = '<symbol> ) </symbol>\n'
    LBRACKET_TOKEN = '<symbol> [ </symbol>\n'
    RBRACKET_TOKEN = '<symbol> ] </symbol>\n'
    SEMICOLON_TOKEN = '<symbol> ; </symbol>\n'
    DOT_TOKEN = '<symbol> . </symbol>\n'
    COMMA_TOKEN = '<symbol> , </symbol>\n'
    MINUS_TOKEN = '<symbol> - </symbol>\n'
    TILDE_TOKEN = '<symbol> ~ </symbol>\n'

    def __init__(self, parser_input: str, parser_output: str) -> None:
        """Initialize the parser with input and output file paths."""
        self.tokens: List[str] = []
        self.token_counter = 0
        self.indent = 0

        # Read tokens from input file
        with open(parser_input) as f:
            tokens_copy = f.readlines()
        
        # Remove <tokens> wrapper
        self.tokens = tokens_copy[1:-1]
        
        self.output = open(parser_output, 'w')
        self.current_token = self.tokens[self.token_counter]
        
        self.compile_class()
        self.output.close()

    def compile_class(self) -> None:
        """Compile a complete class."""
        self.output.write('<class>\n')
        self._increase_indent()
        self._write_and_advance()  # 'class'
        self._write_and_advance()  # className
        self._write_and_advance()  # '{'

        self._compile_class_var_dec()
        self._compile_subroutine()
        
        self._write_indent()
        self.output.write(self.current_token)
        self.output.write('</class>\n')

    def _compile_class_var_dec(self) -> None:
        """Compile class variable declarations."""
        if str(self.current_token) in [self.FIELD_TOKEN, self.STATIC_TOKEN]:
            self._write_indent()
            self.output.write('<classVarDec>\n')
            self._increase_indent()
            
            while str(self.current_token) != self.SEMICOLON_TOKEN:
                self._write_and_advance()
            self._write_and_advance()  # ';'

            self._decrease_indent()
            self._write_indent()
            self.output.write('</classVarDec>\n')
            
            # Recursion for multiple declarations
            if str(self.current_token) in [self.FIELD_TOKEN, self.STATIC_TOKEN]:
                self._compile_class_var_dec()

    def _compile_subroutine(self) -> None:
        """Compile a subroutine (constructor, function, or method)."""
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

        if str(self.current_token) == self.VAR_TOKEN:
            self._compile_var_dec()
        
        self._compile_statements()
        self._write_and_advance()  # '}'
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineBody>\n')
        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineDec>\n')

        # Recursion for multiple subroutines
        if str(self.current_token) in [self.CONSTRUCTOR_TOKEN, self.FUNCTION_TOKEN, self.METHOD_TOKEN]:
            self._compile_subroutine()

    def _compile_parameter_list(self) -> None:
        """Compile a parameter list."""
        self._write_indent()
        self.output.write('<parameterList>\n')
        self._increase_indent()

        while str(self.current_token) != self.RPAREN_TOKEN:
            self._write_and_advance()
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</parameterList>\n')

    def _compile_var_dec(self) -> None:
        """Compile variable declarations."""
        self._write_indent()
        self.output.write('<varDec>\n')
        self._increase_indent()

        while str(self.current_token) != self.SEMICOLON_TOKEN:
            self._write_and_advance()
        
        self._write_and_advance()
        self._decrease_indent()
        self._write_indent()
        self.output.write('</varDec>\n')

        if str(self.current_token) == self.VAR_TOKEN:
            self._compile_var_dec()

    def _compile_statements(self) -> None:
        """Compile statements."""
        self._write_indent()
        self.output.write('<statements>\n')
        self._increase_indent()
        
        while self._check_statement():
            if str(self.current_token) == self.IF_TOKEN:
                self._compile_if()
            elif str(self.current_token) == self.LET_TOKEN:
                self._compile_let()
            elif str(self.current_token) == self.WHILE_TOKEN:
                self._compile_while()
            elif str(self.current_token) == self.DO_TOKEN:
                self._compile_do()
            elif str(self.current_token) == self.RETURN_TOKEN:
                self._compile_return()
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</statements>\n')

    def _compile_do(self) -> None:
        """Compile a do statement."""
        self._write_indent()
        self.output.write('<doStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'do'
        
        # LL(2) look-ahead for subroutine call type
        look_ahead = self.tokens[self.token_counter + 1]
        if look_ahead == self.LPAREN_TOKEN:
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
        """Compile a let statement."""
        self._write_indent()
        self.output.write('<letStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'let'
        self._write_and_advance()  # varName
        
        if str(self.current_token) == self.LBRACKET_TOKEN:
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
        
        if self._check_more_terms():
            self._compile_expression()
        
        self._write_and_advance()  # ';'

        self._decrease_indent()
        self._write_indent()
        self.output.write('</returnStatement>\n')

    def _compile_if(self) -> None:
        """Compile an if statement."""
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
        
        if str(self.current_token) == self.ELSE_TOKEN:
            self._write_and_advance()  # 'else'
            self._write_and_advance()  # '{'
            self._compile_statements()
            self._write_and_advance()  # '}'
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</ifStatement>\n')

    def _compile_expression(self) -> None:
        """Compile an expression."""
        self._write_indent()
        self.output.write('<expression>\n')
        self._increase_indent()

        self._compile_term()
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</expression>\n')

    def _compile_term(self) -> None:
        """Compile a term."""
        self._write_indent()
        self.output.write('<term>\n')
        self._increase_indent()

        token_type = str(self.current_token.split()[0])

        if token_type == '<identifier>':
            look_ahead = self.tokens[self.token_counter + 1]
            if look_ahead == self.LBRACKET_TOKEN:
                self._write_and_advance()  # varName
                self._write_and_advance()  # '['
                self._compile_expression()
                self._write_and_advance()  # ']'
            elif look_ahead == self.LPAREN_TOKEN:
                self._write_and_advance()  # subroutineName
                self._write_and_advance()  # '('
                self._compile_expression_list()
                self._write_and_advance()  # ')'
            elif look_ahead == self.DOT_TOKEN:
                self._write_and_advance()  # className|varName
                self._write_and_advance()  # '.'
                self._write_and_advance()  # subroutineName
                self._write_and_advance()  # '('
                self._compile_expression_list()
                self._write_and_advance()  # ')'
            else:
                self._write_and_advance()  # varName
        elif token_type in ['<integerConstant>', '<stringConstant>']:
            self._write_and_advance()
        elif str(self.current_token) in [self.TRUE_TOKEN, self.FALSE_TOKEN, 
                                          self.NULL_TOKEN, self.THIS_TOKEN]:
            self._write_and_advance()
        elif str(self.current_token) == self.LPAREN_TOKEN:
            self._write_and_advance()  # '('
            self._compile_expression()
            self._write_and_advance()  # ')'
        elif str(self.current_token) in [self.MINUS_TOKEN, self.TILDE_TOKEN]:
            self._write_and_advance()
            self._compile_term()
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</term>\n')

        # Check for operator and more terms
        if self._check_op():
            self._write_and_advance()  # operator
            self._compile_term()

    def _compile_expression_list(self) -> None:
        """Compile an expression list."""
        self._write_indent()
        self.output.write('<expressionList>\n')
        self._increase_indent()
        
        while self._check_more_terms():
            self._compile_expression()
            if str(self.current_token) == self.COMMA_TOKEN:
                self._write_and_advance()  # ','

        self._decrease_indent()
        self._write_indent()
        self.output.write('</expressionList>\n')

    def _write_indent(self) -> None:
        """Write current indentation."""
        self.output.write('  ' * self.indent)

    def _advance(self) -> None:
        """Advance to the next token."""
        self.token_counter += 1
        self.current_token = self.tokens[self.token_counter]

    def _write_and_advance(self) -> None:
        """Write current token and advance."""
        self._write_indent()
        self.output.write(self.current_token)
        self._advance()

    def _increase_indent(self) -> None:
        """Increase indentation level."""
        self.indent += 1

    def _decrease_indent(self) -> None:
        """Decrease indentation level."""
        self.indent -= 1

    def _check_statement(self) -> bool:
        """Check if current token starts a statement."""
        statement_tokens = [self.IF_TOKEN, self.LET_TOKEN, self.WHILE_TOKEN,
                           self.DO_TOKEN, self.RETURN_TOKEN]
        return str(self.current_token) in statement_tokens

    def _check_op(self) -> bool:
        """Check if current token is an operator."""
        op_tokens = [
            '<symbol> + </symbol>\n', '<symbol> - </symbol>\n',
            '<symbol> * </symbol>\n', '<symbol> / </symbol>\n',
            '<symbol> &amp; </symbol>\n', '<symbol> | </symbol>\n',
            '<symbol> &lt; </symbol>\n', '<symbol> &gt; </symbol>\n',
            '<symbol> = </symbol>\n'
        ]
        return str(self.current_token) in op_tokens

    def _check_more_terms(self) -> bool:
        """Check if current token can start a term."""
        token_type = str(self.current_token.split()[0])
        
        if token_type in ['<identifier>', '<integerConstant>', '<stringConstant>']:
            return True
        
        term_tokens = [self.TRUE_TOKEN, self.FALSE_TOKEN, self.NULL_TOKEN,
                       self.THIS_TOKEN, self.LPAREN_TOKEN, self.MINUS_TOKEN,
                       self.TILDE_TOKEN]
        return str(self.current_token) in term_tokens
