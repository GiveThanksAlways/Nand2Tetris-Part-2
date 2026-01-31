"""
Parser module for the Jack compiler.

This module provides parsing functionality for Jack source files,
generating both XML parse trees and VM code output.
"""

from typing import List

from SymbolTable import SymbolTable
from VMWriter import VMWriter

# XML token constants for comparison
KEYWORD_FIELD = '<keyword> field </keyword>\n'
KEYWORD_STATIC = '<keyword> static </keyword>\n'
KEYWORD_VAR = '<keyword> var </keyword>\n'
KEYWORD_CONSTRUCTOR = '<keyword> constructor </keyword>\n'
KEYWORD_FUNCTION = '<keyword> function </keyword>\n'
KEYWORD_METHOD = '<keyword> method </keyword>\n'
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
SYMBOL_DOT = '<symbol> . </symbol>\n'
SYMBOL_COMMA = '<symbol> , </symbol>\n'
SYMBOL_MINUS = '<symbol> - </symbol>\n'
SYMBOL_TILDE = '<symbol> ~ </symbol>\n'
SYMBOL_PLUS = '<symbol> + </symbol>\n'
SYMBOL_STAR = '<symbol> * </symbol>\n'
SYMBOL_SLASH = '<symbol> / </symbol>\n'
SYMBOL_AMP = '<symbol> &amp; </symbol>\n'
SYMBOL_PIPE = '<symbol> | </symbol>\n'
SYMBOL_LT = '<symbol> &lt; </symbol>\n'
SYMBOL_GT = '<symbol> &gt; </symbol>\n'
SYMBOL_EQ = '<symbol> = </symbol>\n'
SYMBOL_CARET = '<symbol> ^ </symbol>\n'


class Parser:
    """
    Parser for Jack source files.

    Parses tokenized Jack code and generates XML parse trees
    and VM code output.
    """

    def __init__(
        self, parser_input: str, parser_output: str, symbol_table: SymbolTable
    ) -> None:
        """
        Initialize the parser with input/output paths and symbol table.

        Args:
            parser_input: Path to the tokenized XML input file.
            parser_output: Base path for output files.
            symbol_table: The symbol table to use for compilation.
        """
        self.tokens_to_parse: List[str] = []
        tokens_copy: List[str] = []
        self.token_counter = 0
        self.indent = 0

        with open(parser_input) as f:
            for line in f:
                tokens_copy.append(line)
        self.tokens_to_parse = tokens_copy[1:-1]

        self.output_file = open(f'{parser_output}.xml', 'w')
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
        self.symbol_table.class_start()
        self.compile_class()

        self.output_file.close()

    def compile_class(self) -> None:
        """Compile a class declaration."""
        self.output_file.write('<class>\n')
        self.increase_indent()
        self.write_and_advance()  # 'class'
        self.class_name = str(self.current_token.split()[1])
        self.write_and_advance()  # className
        self.write_and_advance()  # '{'

        self.compile_class_var_dec()
        self.compile_subroutine()

        self.write_indent()
        self.output_file.write(self.current_token)
        self.output_file.write('</class>\n')

        token_count = len(self.tokens_to_parse)
        if self.token_counter + 1 != token_count:
            look_ahead = str(self.tokens_to_parse[self.token_counter + 1]).split()[1]
            if look_ahead == 'class':
                self.write_and_advance()
                self.compile_class()

    def compile_class_var_dec(self) -> None:
        """Compile class variable declarations (field/static)."""
        if self.current_token in (KEYWORD_FIELD, KEYWORD_STATIC):
            self.write_indent()
            self.output_file.write('<classVarDec>\n')
            self.increase_indent()

            class_var_kind = self.current_token.split()[1]
            class_var_type = self.tokens_to_parse[self.token_counter + 1].split()[1]
            every_two = 0
            start_count = 1

            while self.current_token != SYMBOL_SEMICOLON:
                if every_two % 2 == 0 and start_count > 2:
                    var_name = self.current_token.split()[1]
                    self.symbol_table.define(var_name, class_var_type, class_var_kind)
                self.write_and_advance()
                start_count += 1
                every_two += 1

            self.write_and_advance()  # ';'

            self.decrease_indent()
            self.write_indent()
            self.output_file.write('</classVarDec>\n')

        if self.current_token in (KEYWORD_FIELD, KEYWORD_STATIC):
            self.compile_class_var_dec()

    def compile_subroutine(self) -> None:
        """Compile a subroutine declaration."""
        self.write_indent()
        self.output_file.write('<subroutineDec>\n')
        self.increase_indent()

        self.function_type = str(self.current_token.split()[1])
        self.is_constructor = self.current_token.split()[1] == 'constructor'

        self.write_and_advance()  # constructor|function|method
        self.subroutine_is_void = self.current_token.split()[1] == 'void'

        self.write_and_advance()  # void|type
        self.subroutine_name = str(self.current_token.split()[1])
        self.write_and_advance()  # subroutineName
        self.write_and_advance()  # '('

        self.symbol_table.start_subroutine()
        self.compile_parameter_list()

        self.write_and_advance()  # ')'

        self.write_indent()
        self.output_file.write('<subroutineBody>\n')
        self.increase_indent()
        self.write_and_advance()  # '{'

        if self.current_token == KEYWORD_VAR:
            self.compile_var_dec()

        num_locals = self.symbol_table.var_count('var')
        self.vm_writer.write_function(self.class_name, self.subroutine_name, num_locals)

        if self.is_constructor:
            self.vm_writer.write_push('constant', self.symbol_table.var_count('field'))
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        elif self.function_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)
            self.symbol_table.define_method('this', self.class_name, 'argument')

        self.compile_statements()

        self.write_and_advance()  # '}'
        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</subroutineBody>\n')
        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</subroutineDec>\n')

        self.symbol_table.define_subroutine_tracker(
            self.subroutine_name, 'method', self.class_name, self.subroutine_is_void
        )

        if self.current_token in (KEYWORD_CONSTRUCTOR, KEYWORD_FUNCTION, KEYWORD_METHOD):
            self.compile_subroutine()

    def compile_parameter_list(self) -> None:
        """Compile a parameter list."""
        self.write_indent()
        self.output_file.write('<parameterList>\n')
        self.increase_indent()

        every_three = 0
        while self.current_token != SYMBOL_CLOSE_PAREN:
            if every_three % 3 == 0:
                param_name = self.tokens_to_parse[self.token_counter + 1].split()[1]
                param_type = self.tokens_to_parse[self.token_counter].split()[1]
                self.symbol_table.define_method(param_name, param_type, 'argument')
            self.write_and_advance()
            every_three += 1

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</parameterList>\n')

    def compile_var_dec(self) -> None:
        """Compile a variable declaration."""
        self.write_indent()
        self.output_file.write('<varDec>\n')
        self.increase_indent()

        self.write_and_advance()  # 'var'
        every_two = 0
        var_type = self.tokens_to_parse[self.token_counter].split()[1]
        self.write_and_advance()  # type

        while self.current_token != SYMBOL_SEMICOLON:
            if every_two % 2 == 0:
                var_name = self.tokens_to_parse[self.token_counter].split()[1]
                self.symbol_table.define_method(var_name, var_type, 'var')
            self.write_and_advance()
            every_two += 1

        self.write_and_advance()  # ';'
        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</varDec>\n')

        if self.current_token == KEYWORD_VAR:
            self.compile_var_dec()

    def compile_statements(self) -> None:
        """Compile a sequence of statements."""
        self.write_indent()
        self.output_file.write('<statements>\n')
        self.increase_indent()

        while self.check_is_statement():
            if self.current_token == KEYWORD_IF:
                self.compile_if()
            elif self.current_token == KEYWORD_LET:
                self.compile_let()
            elif self.current_token == KEYWORD_WHILE:
                self.compile_while()
            elif self.current_token == KEYWORD_DO:
                self.compile_do()
            elif self.current_token == KEYWORD_RETURN:
                self.compile_return()

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</statements>\n')

    def compile_do(self) -> None:
        """Compile a do statement."""
        self.write_indent()
        self.output_file.write('<doStatement>\n')
        self.increase_indent()

        self.write_and_advance()  # 'do'

        look_ahead = self.tokens_to_parse[self.token_counter + 1]
        if look_ahead == SYMBOL_OPEN_PAREN:
            call_func = str(self.current_token.split()[1])
            self.vm_writer.write_push('pointer', '0')
            self.write_and_advance()  # subroutineName
            self.write_and_advance()  # '('
            self.compile_expression_list()
            self.write_and_advance()  # ')'
            self.write_and_advance()  # ';'
            num_args = self.symbol_table.get_id(call_func)
            self.vm_writer.write_call(f'{self.class_name}.{call_func}', num_args)
            if self.symbol_table.get_void(call_func):
                self.vm_writer.write_pop('temp', '0')
        else:
            other_class_name = str(self.current_token.split()[1])
            self.write_and_advance()  # className|varName
            self.write_and_advance()  # '.'
            call_func = str(self.current_token.split()[1])
            self.write_and_advance()  # subroutineName
            self.write_and_advance()  # '('
            self.compile_expression_list()
            self.write_and_advance()  # ')'
            self.write_and_advance()  # ';'
            num_args = self.symbol_table.get_id(call_func)

            if self.symbol_table.get_kind(other_class_name) is None:
                self.vm_writer.write_call(f'{other_class_name}.{call_func}', num_args)
                if self.symbol_table.get_void(call_func):
                    self.vm_writer.write_pop('temp', '0')
            else:
                segment = self.symbol_table.get_kind(other_class_name)
                index = self.symbol_table.get_id(other_class_name)
                self.vm_writer.write_push(segment, index)
                self.vm_writer.write_call(f'{other_class_name}.{call_func}', num_args)
                if self.symbol_table.get_void(call_func):
                    self.vm_writer.write_pop('temp', '0')

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</doStatement>\n')

    def compile_let(self) -> None:
        """Compile a let statement."""
        self.write_indent()
        self.output_file.write('<letStatement>\n')
        self.increase_indent()

        self.write_and_advance()  # 'let'
        let_var_name = str(self.current_token.split()[1])
        self.write_and_advance()  # varName

        if self.current_token == SYMBOL_OPEN_BRACKET:
            self.is_array = True
            segment = self.symbol_table.get_kind(let_var_name)
            index = self.symbol_table.get_id(let_var_name)
            self.vm_writer.write_push(segment, index)
            self.write_and_advance()  # '['
            self.compile_expression()
            self.write_and_advance()  # ']'
            self.vm_writer.write_arithmetic('+')

        self.write_and_advance()  # '='
        self.compile_expression()
        self.write_and_advance()  # ';'

        if self.is_array:
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
            self.is_array = False
        else:
            segment = self.symbol_table.get_kind(let_var_name)
            index = self.symbol_table.get_id(let_var_name)
            self.vm_writer.write_pop(segment, index)

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</letStatement>\n')

    def compile_while(self) -> None:
        """Compile a while statement."""
        self.write_indent()
        self.output_file.write('<whileStatement>\n')
        self.increase_indent()

        while_label_1 = f'whileL{self.while_label_counter}'
        self.while_label_counter += 1
        while_label_2 = f'whileL{self.while_label_counter}'
        self.while_label_counter += 1
        self.vm_writer.write_label(while_label_1)

        self.write_and_advance()  # 'while'
        self.write_and_advance()  # '('
        self.compile_expression()

        self.vm_writer.write_arithmetic('NOT')
        self.vm_writer.write_if(while_label_2)

        self.write_and_advance()  # ')'
        self.write_and_advance()  # '{'
        self.compile_statements()
        self.write_and_advance()  # '}'

        self.vm_writer.write_goto(while_label_1)
        self.vm_writer.write_label(while_label_2)

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</whileStatement>\n')

    def compile_return(self) -> None:
        """Compile a return statement."""
        self.write_indent()
        self.output_file.write('<returnStatement>\n')
        self.increase_indent()

        self.write_and_advance()  # 'return'

        if self.check_has_more_terms():
            self.compile_expression()
        self.write_and_advance()  # ';'

        if self.subroutine_is_void:
            self.vm_writer.write_push('constant', 0)
        self.vm_writer.write_return()

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</returnStatement>\n')

    def compile_if(self) -> None:
        """Compile an if statement."""
        self.write_indent()
        self.output_file.write('<ifStatement>\n')
        self.increase_indent()

        self.write_and_advance()  # 'if'
        self.write_and_advance()  # '('
        self.compile_expression()
        self.write_and_advance()  # ')'

        self.vm_writer.write_arithmetic('NOT')
        if_label_1 = f'ifL{self.if_label_counter}'
        self.if_label_counter += 1
        self.vm_writer.write_if(if_label_1)

        self.write_and_advance()  # '{'
        self.compile_statements()

        if_label_2 = f'ifL{self.if_label_counter}'
        self.if_label_counter += 1
        self.vm_writer.write_goto(if_label_2)

        self.vm_writer.write_label(if_label_1)
        self.write_and_advance()  # '}'

        if self.current_token == KEYWORD_ELSE:
            self.write_and_advance()  # 'else'
            self.write_and_advance()  # '{'
            self.compile_statements()
            self.write_and_advance()  # '}'

        self.vm_writer.write_label(if_label_2)

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</ifStatement>\n')

    def compile_expression(self) -> None:
        """Compile an expression."""
        self.write_indent()
        self.output_file.write('<expression>\n')
        self.increase_indent()

        self.compile_term()

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</expression>\n')

    def compile_term(self) -> None:
        """Compile a term."""
        self.write_indent()
        self.output_file.write('<term>\n')
        self.increase_indent()

        token_tag = str(self.current_token.split()[0])
        vm_token = str(self.current_token.split()[1])

        if token_tag == '<identifier>':
            look_ahead = self.tokens_to_parse[self.token_counter + 1]
            if look_ahead == SYMBOL_OPEN_BRACKET:  # array access
                segment = self.symbol_table.get_kind(vm_token)
                index = self.symbol_table.get_id(vm_token)
                self.vm_writer.write_push(segment, index)
                self.write_and_advance()  # varName
                self.write_and_advance()  # '['
                self.compile_expression()
                self.write_and_advance()  # ']'
                self.vm_writer.write_arithmetic('+')
                self.vm_writer.write_pop('pointer', '1')
                self.vm_writer.write_push('that', '0')
            elif look_ahead == SYMBOL_OPEN_PAREN:  # subroutine call
                call_func = str(self.current_token.split()[1])
                self.vm_writer.write_push('argument', '0')
                self.write_and_advance()  # subroutineName
                self.write_and_advance()  # '('
                self.compile_expression_list()
                self.write_and_advance()  # ')'
                num_args = self.symbol_table.get_id(call_func)
                self.vm_writer.write_call(f'{self.class_name}.{call_func}', num_args)
                if self.symbol_table.get_void(call_func):
                    self.vm_writer.write_pop('temp', '0')
            elif look_ahead == SYMBOL_DOT:  # method call
                other_class_name = str(self.current_token.split()[1])
                self.write_and_advance()  # className|varName
                self.write_and_advance()  # '.'
                call_func = str(self.current_token.split()[1])
                self.write_and_advance()  # subroutineName
                self.write_and_advance()  # '('
                self.compile_expression_list()
                self.write_and_advance()  # ')'
                num_args = self.symbol_table.get_id(call_func)
                self.vm_writer.write_call(f'{other_class_name}.{call_func}', num_args)
            else:  # simple varName
                segment = self.symbol_table.get_kind(vm_token)
                index = self.symbol_table.get_id(vm_token)
                self.vm_writer.write_push(segment, index)
                self.write_and_advance()
        elif token_tag == '<integerConstant>':
            self.vm_writer.write_push('constant', vm_token)
            self.write_and_advance()
        elif token_tag == '<stringConstant>':
            token_parts = self.current_token.split()
            each_letter = list(' '.join(token_parts[1:-1]))
            self.vm_writer.write_push('constant', len(each_letter))
            self.vm_writer.write_call('String.new', 1)
            for letter in each_letter:
                self.vm_writer.write_push('constant', ord(letter))
                self.vm_writer.write_call('String.appendChar', 2)
            self.write_and_advance()
        elif self.current_token == KEYWORD_TRUE:
            self.vm_writer.write_push('constant', 1)
            self.vm_writer.write_arithmetic('NEG')
            self.write_and_advance()
        elif self.current_token == KEYWORD_FALSE:
            self.vm_writer.write_push('constant', 0)
            self.write_and_advance()
        elif self.current_token == KEYWORD_NULL:
            self.vm_writer.write_push('constant', 0)
            self.write_and_advance()
        elif self.current_token == KEYWORD_THIS:
            self.vm_writer.write_push('pointer', 0)
            self.write_and_advance()
        elif self.current_token == SYMBOL_OPEN_PAREN:
            self.write_and_advance()  # '('
            self.compile_expression()
            self.write_and_advance()  # ')'
        elif self.current_token == SYMBOL_MINUS:
            self.write_and_advance()
            self.compile_term()
            self.vm_writer.write_arithmetic('NEG')
        elif self.current_token == SYMBOL_TILDE:
            self.write_and_advance()
            self.compile_term()
            self.vm_writer.write_arithmetic('~')

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</term>\n')

        if self.check_is_operator():
            op_term = str(self.current_token.split()[1])
            self.write_and_advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(op_term)

    def compile_expression_list(self) -> None:
        """Compile an expression list."""
        self.write_indent()
        self.output_file.write('<expressionList>\n')
        self.increase_indent()

        while self.check_has_more_terms():
            self.compile_expression()
            if self.current_token == SYMBOL_COMMA:
                self.write_and_advance()

        self.decrease_indent()
        self.write_indent()
        self.output_file.write('</expressionList>\n')

    def write_indent(self) -> None:
        """Write current indentation to output."""
        for _ in range(self.indent):
            self.output_file.write('  ')

    def advance(self) -> None:
        """Advance to the next token."""
        self.token_counter += 1
        self.current_token = self.tokens_to_parse[self.token_counter]

    def write_and_advance(self) -> None:
        """Write current token to output and advance."""
        self.write_indent()
        self.output_file.write(self.current_token)
        self.advance()

    def increase_indent(self) -> None:
        """Increase the indentation level."""
        self.indent += 1

    def decrease_indent(self) -> None:
        """Decrease the indentation level."""
        self.indent -= 1

    def check_is_statement(self) -> bool:
        """Check if current token is a statement keyword."""
        statement_keywords = [
            KEYWORD_IF, KEYWORD_LET, KEYWORD_WHILE, KEYWORD_DO, KEYWORD_RETURN
        ]
        return self.current_token in statement_keywords

    def check_is_operator(self) -> bool:
        """Check if current token is an operator."""
        operators = [
            SYMBOL_PLUS, SYMBOL_MINUS, SYMBOL_STAR, SYMBOL_SLASH,
            SYMBOL_AMP, SYMBOL_PIPE, SYMBOL_LT, SYMBOL_GT, SYMBOL_EQ, SYMBOL_CARET
        ]
        return self.current_token in operators

    def check_has_more_terms(self) -> bool:
        """Check if there are more terms to parse."""
        token_tag = str(self.current_token.split()[0])

        if token_tag in ('<identifier>', '<integerConstant>', '<stringConstant>'):
            return True

        term_keywords = [KEYWORD_TRUE, KEYWORD_FALSE, KEYWORD_NULL, KEYWORD_THIS]
        term_symbols = [SYMBOL_OPEN_PAREN, SYMBOL_MINUS, SYMBOL_TILDE]

        return self.current_token in term_keywords or self.current_token in term_symbols
    
