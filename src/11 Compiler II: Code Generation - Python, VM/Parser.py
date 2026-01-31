"""
Parser module for the Jack compiler.

This module implements a recursive descent parser that translates tokenized
Jack source code into XML parse trees and VM code.
"""

from typing import List

from SymbolTable import SymbolTable
from VMWriter import VMWriter

# XML token patterns for comparison
KEYWORD_FIELD = '<keyword> field </keyword>\n'
KEYWORD_STATIC = '<keyword> static </keyword>\n'
KEYWORD_CONSTRUCTOR = '<keyword> constructor </keyword>\n'
KEYWORD_FUNCTION = '<keyword> function </keyword>\n'
KEYWORD_METHOD = '<keyword> method </keyword>\n'
KEYWORD_VAR = '<keyword> var </keyword>\n'
KEYWORD_IF = '<keyword> if </keyword>\n'
KEYWORD_LET = '<keyword> let </keyword>\n'
KEYWORD_WHILE = '<keyword> while </keyword>\n'
KEYWORD_DO = '<keyword> do </keyword>\n'
KEYWORD_RETURN = '<keyword> return </keyword>\n'
KEYWORD_ELSE = '<keyword> else </keyword>\n'
KEYWORD_TRUE = '<keyword> true </keyword>\n'
KEYWORD_FALSE = '<keyword> false </keyword>\n'
KEYWORD_NULL = '<keyword> null </keyword>\n'
KEYWORD_THIS = '<keyword> this </keyword>\n'

SYMBOL_SEMICOLON = '<symbol> ; </symbol>\n'
SYMBOL_CLOSE_PAREN = '<symbol> ) </symbol>\n'
SYMBOL_OPEN_PAREN = '<symbol> ( </symbol>\n'
SYMBOL_OPEN_BRACKET = '<symbol> [ </symbol>\n'
SYMBOL_CLOSE_BRACKET = '<symbol> ] </symbol>\n'
SYMBOL_DOT = '<symbol> . </symbol>\n'
SYMBOL_COMMA = '<symbol> , </symbol>\n'
SYMBOL_MINUS = '<symbol> - </symbol>\n'
SYMBOL_TILDE = '<symbol> ~ </symbol>\n'

# Operator symbols for expression parsing
OPERATOR_TOKENS = [
    '<symbol> + </symbol>\n',
    '<symbol> - </symbol>\n',
    '<symbol> * </symbol>\n',
    '<symbol> / </symbol>\n',
    '<symbol> &amp; </symbol>\n',
    '<symbol> | </symbol>\n',
    '<symbol> &lt; </symbol>\n',
    '<symbol> &gt; </symbol>\n',
    '<symbol> = </symbol>\n',
    '<symbol> ^ </symbol>\n',
]


class Parser:
    """
    Recursive descent parser for Jack language.

    Parses tokenized Jack code and generates both XML parse trees
    and VM bytecode output.
    """

    def __init__(self, parser_input: str, parser_output: str,
                 symbol_table: SymbolTable):
        """
        Initialize the parser with input tokens and output paths.

        Args:
            parser_input: Path to the tokenized XML input file.
            parser_output: Base path for output files.
            symbol_table: The symbol table to use for compilation.
        """
        self.tokens_to_parse: List[str] = []
        self.token_counter = 0
        self.indent = 0

        with open(parser_input) as f:
            tokens_copy = [line for line in f]
        self.tokens_to_parse = tokens_copy[1:-1]

        self.output = open(f'{parser_output}.xml', 'w')
        self.vm_writer = VMWriter(parser_output)

        self.current_token_arr = self.tokens_to_parse[self.token_counter].split(' ')
        self.current_token = self.tokens_to_parse[self.token_counter]
        self.class_name = ''
        self.subroutine_is_void = False
        self.if_label_counter = 0
        self.while_label_counter = 0
        self.is_constructor = False
        self.function_type = ''
        self.subroutine_name = ''
        self.is_array = False

        self.symbol_table = symbol_table
        self.symbol_table.classStart()
        self.compile_class()

        self.output.close()

    def compile_class(self) -> None:
        """Compile a complete class definition."""
        self.output.write('<class>\n')
        self._increase_indent()
        self._write_and_advance()
        self.class_name = str(self.current_token.split()[1])
        self._write_and_advance()
        self._write_and_advance()
        self._compile_class_var_dec()
        self._compile_subroutine()
        self._write_indent()
        self.output.write(self.current_token)
        self.output.write('</class>\n')

        list_size = len(self.tokens_to_parse)
        if self.token_counter + 1 != list_size:
            look_ahead = str(self.tokens_to_parse[self.token_counter + 1]).split()[1]
            if look_ahead == 'class':
                self._write_and_advance()
                self.compile_class()

    def _compile_class_var_dec(self) -> None:
        """Compile class variable declarations (field/static)."""
        if self.current_token not in (KEYWORD_FIELD, KEYWORD_STATIC):
            return

        self._write_indent()
        self.output.write('<classVarDec>\n')
        self._increase_indent()

        var_kind = self.current_token.split()[1]
        var_type = self.tokens_to_parse[self.token_counter + 1].split()[1]
        every_two = 0
        start = 1

        while self.current_token != SYMBOL_SEMICOLON:
            if every_two % 2 == 0 and start > 2:
                var_name = self.current_token.split()[1]
                self.symbol_table.define(var_name, var_type, var_kind)
            self._write_and_advance()
            start += 1
            every_two += 1

        self._write_and_advance()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</classVarDec>\n')

        if self.current_token in (KEYWORD_FIELD, KEYWORD_STATIC):
            self._compile_class_var_dec()

    def _compile_subroutine(self) -> None:
        """Compile a subroutine (constructor/function/method)."""
        self._write_indent()
        self.output.write('<subroutineDec>\n')
        self._increase_indent()

        self.function_type = str(self.current_token.split()[1])
        self.is_constructor = (self.function_type == 'constructor')

        self._write_and_advance()
        self.subroutine_is_void = (self.current_token.split()[1] == 'void')

        self._write_and_advance()
        self.subroutine_name = str(self.current_token.split()[1])
        self._write_and_advance()
        self._write_and_advance()

        self.symbol_table.startSubroutine()
        if self.function_type == 'method':
            self.symbol_table.defineMethod('this', self.class_name, 'argument')

        self._compile_parameter_list()
        self._write_and_advance()

        self._write_indent()
        self.output.write('<subroutineBody>\n')
        self._increase_indent()
        self._write_and_advance()

        if self.current_token == KEYWORD_VAR:
            self._compile_var_dec()

        num_locals = self.symbol_table.varCount('var')
        self.vm_writer.writeFunction(self.class_name, self.subroutine_name, num_locals)

        if self.is_constructor:
            self.vm_writer.writePush('constant', self.symbol_table.varCount('field'))
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)
        elif self.function_type == 'method':
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)

        self._compile_statements()
        self._write_and_advance()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineBody>\n')
        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineDec>\n')

        self.symbol_table.defineSubroutineTracker(
            self.subroutine_name, 'method', self.class_name, self.subroutine_is_void)

        if self.current_token in (KEYWORD_CONSTRUCTOR, KEYWORD_FUNCTION, KEYWORD_METHOD):
            self._compile_subroutine()

    def _compile_parameter_list(self) -> None:
        """Compile a parameter list."""
        self._write_indent()
        self.output.write('<parameterList>\n')
        self._increase_indent()

        every_three = 0
        while self.current_token != SYMBOL_CLOSE_PAREN:
            if every_three % 3 == 0:
                param_name = self.tokens_to_parse[self.token_counter + 1].split()[1]
                param_type = self.tokens_to_parse[self.token_counter].split()[1]
                self.symbol_table.defineMethod(param_name, param_type, 'argument')
            self._write_and_advance()
            every_three += 1

        self._decrease_indent()
        self._write_indent()
        self.output.write('</parameterList>\n')

    def _compile_var_dec(self) -> None:
        """Compile a variable declaration."""
        self._write_indent()
        self.output.write('<varDec>\n')
        self._increase_indent()

        self._write_and_advance()
        every_two = 0
        var_type = self.tokens_to_parse[self.token_counter].split()[1]
        self._write_and_advance()

        while self.current_token != SYMBOL_SEMICOLON:
            if every_two % 2 == 0:
                var_name = self.tokens_to_parse[self.token_counter].split()[1]
                self.symbol_table.defineMethod(var_name, var_type, 'var')
            self._write_and_advance()
            every_two += 1

        self._write_and_advance()
        self._decrease_indent()
        self._write_indent()
        self.output.write('</varDec>\n')

        if self.current_token == KEYWORD_VAR:
            self._compile_var_dec()

    def _compile_statements(self) -> None:
        """Compile a sequence of statements."""
        self._write_indent()
        self.output.write('<statements>\n')
        self._increase_indent()

        while self._is_statement():
            if self.current_token == KEYWORD_IF:
                self._compile_if()
            elif self.current_token == KEYWORD_LET:
                self._compile_let()
            elif self.current_token == KEYWORD_WHILE:
                self._compile_while()
            elif self.current_token == KEYWORD_DO:
                self._compile_do()
            elif self.current_token == KEYWORD_RETURN:
                self._compile_return()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</statements>\n')

    def _compile_do(self) -> None:
        """Compile a do statement (subroutine call)."""
        self._write_indent()
        self.output.write('<doStatement>\n')
        self._increase_indent()

        self._write_and_advance()

        look_ahead = self.tokens_to_parse[self.token_counter + 1]
        if look_ahead == SYMBOL_OPEN_PAREN:
            call_name = str(self.current_token.split()[1])
            self.vm_writer.writePush('pointer', '0')
            self._write_and_advance()
            self._write_and_advance()
            self._compile_expression_list()
            self._write_and_advance()
            self._write_and_advance()

            num_args = self.symbol_table.getIDofClass(call_name, self.class_name)
            self.vm_writer.writeCall(f'{self.class_name}.{call_name}', str(num_args))

            if self.symbol_table.getVoid(call_name, self.class_name):
                self.vm_writer.writePop('temp', '0')
        else:
            other_class_name = str(self.current_token.split()[1])
            self._write_and_advance()
            self._write_and_advance()
            call_name = str(self.current_token.split()[1])

            if self.symbol_table.getKind(other_class_name) is not None:
                segment = self.symbol_table.getKind(other_class_name)
                index = self.symbol_table.getID(other_class_name)
                self.vm_writer.writePush(segment, index)

            self._write_and_advance()
            self._write_and_advance()
            self._compile_expression_list()
            self._write_and_advance()
            self._write_and_advance()

            if self.symbol_table.getKind(other_class_name) is None:
                num_args = self.symbol_table.getIDofClass(call_name, other_class_name)
                self.vm_writer.writeCall(f'{other_class_name}.{call_name}', str(num_args))
                if self.symbol_table.getVoid(call_name, other_class_name):
                    self.vm_writer.writePop('temp', '0')
            else:
                real_class_name = self.symbol_table.getType(other_class_name)
                if real_class_name is not None:
                    num_args = self.symbol_table.getIDofClass(call_name, real_class_name)
                    self.vm_writer.writeCall(f'{real_class_name}.{call_name}', str(num_args))
                    if self.symbol_table.getVoid(call_name, real_class_name):
                        self.vm_writer.writePop('temp', '0')
                else:
                    num_args = self.symbol_table.getIDofClass(call_name, other_class_name)
                    self.vm_writer.writeCall(f'{other_class_name}.{call_name}', str(num_args))
                    if self.symbol_table.getVoid(call_name, other_class_name):
                        self.vm_writer.writePop('temp', '0')

        self._decrease_indent()
        self._write_indent()
        self.output.write('</doStatement>\n')

    def _compile_let(self) -> None:
        """Compile a let statement."""
        self._write_indent()
        self.output.write('<letStatement>\n')
        self._increase_indent()

        self._write_and_advance()
        var_name = str(self.current_token.split()[1])
        self._write_and_advance()

        if self.current_token == SYMBOL_OPEN_BRACKET:
            self.is_array = True
            segment = self.symbol_table.getKind(var_name)
            index = self.symbol_table.getID(var_name)
            self.vm_writer.writePush(segment, index)
            self._write_and_advance()
            self._compile_expression()
            self._write_and_advance()
            self.vm_writer.writeArithmetic('+')

        self._write_and_advance()
        self._compile_expression()
        self._write_and_advance()

        if self.is_array:
            self.vm_writer.writePop('temp', 0)
            self.vm_writer.writePop('pointer', 1)
            self.vm_writer.writePush('temp', 0)
            self.vm_writer.writePop('that', 0)
            self.is_array = False
        else:
            segment = self.symbol_table.getKind(var_name)
            index = self.symbol_table.getID(var_name)
            self.vm_writer.writePop(segment, index)

        self._decrease_indent()
        self._write_indent()
        self.output.write('</letStatement>\n')

    def _compile_while(self) -> None:
        """Compile a while statement."""
        self._write_indent()
        self.output.write('<whileStatement>\n')
        self._increase_indent()

        label1 = f'whileL{self.while_label_counter}'
        self.while_label_counter += 1
        label2 = f'whileL{self.while_label_counter}'
        self.while_label_counter += 1

        self.vm_writer.writeLabel(label1)

        self._write_and_advance()
        self._write_and_advance()
        self._compile_expression()

        self.vm_writer.writeArithmetic('NOT')
        self.vm_writer.writeIf(label2)

        self._write_and_advance()
        self._write_and_advance()
        self._compile_statements()
        self._write_and_advance()

        self.vm_writer.writeGoto(label1)
        self.vm_writer.writeLabel(label2)

        self._decrease_indent()
        self._write_indent()
        self.output.write('</whileStatement>\n')

    def _compile_return(self) -> None:
        """Compile a return statement."""
        self._write_indent()
        self.output.write('<returnStatement>\n')
        self._increase_indent()

        self._write_and_advance()

        if self._has_more_terms():
            self._compile_expression()
        self._write_and_advance()

        if self.subroutine_is_void:
            self.vm_writer.writePush('constant', 0)
        self.vm_writer.writeReturn()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</returnStatement>\n')

    def _compile_if(self) -> None:
        """Compile an if statement."""
        self._write_indent()
        self.output.write('<ifStatement>\n')
        self._increase_indent()

        self._write_and_advance()
        self._write_and_advance()
        self._compile_expression()
        self._write_and_advance()

        self.vm_writer.writeArithmetic('NOT')
        label1 = f'ifL{self.if_label_counter}'
        self.if_label_counter += 1
        self.vm_writer.writeIf(label1)

        self._write_and_advance()
        self._compile_statements()

        label2 = f'ifL{self.if_label_counter}'
        self.if_label_counter += 1
        self.vm_writer.writeGoto(label2)

        self.vm_writer.writeLabel(label1)
        self._write_and_advance()

        if self.current_token == KEYWORD_ELSE:
            self._write_and_advance()
            self._write_and_advance()
            self._compile_statements()
            self._write_and_advance()

        self.vm_writer.writeLabel(label2)

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

        token_tag = str(self.current_token.split()[0])
        token_value = str(self.current_token.split()[1])

        if token_tag == '<identifier>':
            look_ahead = self.tokens_to_parse[self.token_counter + 1]

            if look_ahead == SYMBOL_OPEN_BRACKET:
                segment = self.symbol_table.getKind(token_value)
                index = self.symbol_table.getID(token_value)
                self.vm_writer.writePush(segment, index)
                self._write_and_advance()
                self._write_and_advance()
                self._compile_expression()
                self._write_and_advance()
                self.vm_writer.writeArithmetic('+')
                self.vm_writer.writePop('pointer', '1')
                self.vm_writer.writePush('that', '0')

            elif look_ahead == SYMBOL_OPEN_PAREN:
                call_name = str(self.current_token.split()[1])
                self.vm_writer.writePush('argument', '0')
                self._write_and_advance()
                self._write_and_advance()
                self._compile_expression_list()
                self._write_and_advance()
                num_args = self.symbol_table.getIDofClass(call_name, self.class_name)
                self.vm_writer.writeCall(f'{self.class_name}.{call_name}', str(num_args))
                if self.symbol_table.getVoid(call_name, self.class_name):
                    self.vm_writer.writePop('temp', '0')

            elif look_ahead == SYMBOL_DOT:
                other_class_name = str(self.current_token.split()[1])
                self._write_and_advance()
                self._write_and_advance()
                call_name = str(self.current_token.split()[1])
                self._write_and_advance()
                self._write_and_advance()
                self._compile_expression_list()
                self._write_and_advance()

                real_class_name = self.symbol_table.getType(other_class_name)

                if self.symbol_table.getID(other_class_name) is not None:
                    self.vm_writer.writePush(
                        self.symbol_table.getKind(other_class_name),
                        self.symbol_table.getID(other_class_name))

                if real_class_name is not None:
                    num_args = self.symbol_table.getIDofClass(call_name, real_class_name)
                    self.vm_writer.writeCall(f'{real_class_name}.{call_name}', str(num_args))
                    if self.symbol_table.getVoid(call_name, real_class_name):
                        self.vm_writer.writePop('temp', '0')
                else:
                    num_args = self.symbol_table.getIDofClass(call_name, other_class_name)
                    self.vm_writer.writeCall(f'{other_class_name}.{call_name}', str(num_args))
                    if self.symbol_table.getVoid(call_name, other_class_name):
                        self.vm_writer.writePop('temp', '0')
            else:
                segment = self.symbol_table.getKind(token_value)
                index = self.symbol_table.getID(token_value)
                self.vm_writer.writePush(segment, index)
                self._write_and_advance()

        elif token_tag == '<integerConstant>':
            self.vm_writer.writePush('constant', token_value)
            self._write_and_advance()

        elif token_tag == '<stringConstant>':
            token_parts = self.current_token.split()
            letters = list(' '.join(token_parts[1:-1]))
            self.vm_writer.writePush('constant', len(letters))
            self.vm_writer.writeCall('String.new', 1)
            for char in letters:
                self.vm_writer.writePush('constant', ord(char))
                self.vm_writer.writeCall('String.appendChar', 2)
            self._write_and_advance()

        elif self.current_token == KEYWORD_TRUE:
            self.vm_writer.writePush('constant', 1)
            self.vm_writer.writeArithmetic('NEG')
            self._write_and_advance()

        elif self.current_token == KEYWORD_FALSE:
            self.vm_writer.writePush('constant', 0)
            self._write_and_advance()

        elif self.current_token == KEYWORD_NULL:
            self.vm_writer.writePush('constant', 0)
            self._write_and_advance()

        elif self.current_token == KEYWORD_THIS:
            self.vm_writer.writePush('pointer', 0)
            self._write_and_advance()

        elif self.current_token == SYMBOL_OPEN_PAREN:
            self._write_and_advance()
            self._compile_expression()
            self._write_and_advance()

        elif self.current_token == SYMBOL_MINUS:
            self._write_and_advance()
            self._compile_term()
            self.vm_writer.writeArithmetic('NEG')

        elif self.current_token == SYMBOL_TILDE:
            self._write_and_advance()
            self._compile_term()
            self.vm_writer.writeArithmetic('~')

        self._decrease_indent()
        self._write_indent()
        self.output.write('</term>\n')

        if self._is_operator():
            operator = str(self.current_token.split()[1])
            self._write_and_advance()
            self._compile_term()
            self.vm_writer.writeArithmetic(operator)

    def _compile_expression_list(self) -> None:
        """Compile a comma-separated list of expressions."""
        self._write_indent()
        self.output.write('<expressionList>\n')
        self._increase_indent()

        while self._has_more_terms():
            self._compile_expression()
            if self.current_token == SYMBOL_COMMA:
                self._write_and_advance()

        self._decrease_indent()
        self._write_indent()
        self.output.write('</expressionList>\n')

    def _write_indent(self) -> None:
        """Write indentation to output."""
        for _ in range(self.indent):
            self.output.write('  ')

    def _advance(self) -> None:
        """Advance to the next token."""
        self.token_counter += 1
        self.current_token = self.tokens_to_parse[self.token_counter]

    def _write_and_advance(self) -> None:
        """Write current token to output and advance."""
        self._write_indent()
        self.output.write(self.current_token)
        self._advance()

    def _increase_indent(self) -> None:
        """Increase indentation level."""
        self.indent += 1

    def _decrease_indent(self) -> None:
        """Decrease indentation level."""
        self.indent -= 1

    def _is_statement(self) -> bool:
        """Check if current token starts a statement."""
        return self.current_token in (
            KEYWORD_IF, KEYWORD_LET, KEYWORD_WHILE,
            KEYWORD_DO, KEYWORD_RETURN
        )

    def _is_operator(self) -> bool:
        """Check if current token is an operator."""
        return self.current_token in OPERATOR_TOKENS

    def _has_more_terms(self) -> bool:
        """Check if there are more terms to parse."""
        token_tag = str(self.current_token.split()[0])

        if token_tag in ('<identifier>', '<integerConstant>', '<stringConstant>'):
            return True
        if self.current_token in (KEYWORD_TRUE, KEYWORD_FALSE, KEYWORD_NULL,
                                   KEYWORD_THIS, SYMBOL_OPEN_PAREN,
                                   SYMBOL_MINUS, SYMBOL_TILDE):
            return True
        return False

    # Backwards compatibility - public method names
    compileClass = compile_class
