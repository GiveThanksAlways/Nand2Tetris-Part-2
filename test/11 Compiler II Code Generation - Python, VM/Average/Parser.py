"""
Parser module for the Jack compiler.

This module provides the Parser class for parsing tokenized Jack code,
generating XML parse trees, and producing VM code output.
"""

from typing import List, Optional

from SymbolTable import SymbolTable
from VMWriter import VMWriter

# Token patterns for statement keywords
STATEMENT_TOKENS: List[str] = [
    '<keyword> if </keyword>\n',
    '<keyword> let </keyword>\n',
    '<keyword> while </keyword>\n',
    '<keyword> do </keyword>\n',
    '<keyword> return </keyword>\n'
]

# Token patterns for operators
OPERATOR_TOKENS: List[str] = [
    '<symbol> + </symbol>\n',
    '<symbol> - </symbol>\n',
    '<symbol> * </symbol>\n',
    '<symbol> / </symbol>\n',
    '<symbol> &amp; </symbol>\n',
    '<symbol> | </symbol>\n',
    '<symbol> &lt; </symbol>\n',
    '<symbol> &gt; </symbol>\n',
    '<symbol> = </symbol>\n',
    '<symbol> ^ </symbol>\n'
]


class Parser:
    """
    Parser for the Jack language.

    Parses tokenized Jack source code and generates both XML parse trees
    and VM code output.
    """

    def __init__(
        self,
        parser_input: str,
        parser_output: str,
        symbol_table: SymbolTable
    ) -> None:
        """
        Initialize the parser with input/output paths and symbol table.

        Args:
            parser_input: Path to the tokenized XML input file.
            parser_output: Base path for output files.
            symbol_table: The symbol table to use for compilation.
        """
        self.tokens_to_parse: List[str] = []
        self.tokens_copy: List[str] = []
        self.token_counter: int = 0
        self.indent: int = 0

        # Open the input XML file made by the tokenizer
        with open(parser_input) as f:
            for line in f:
                self.tokens_copy.append(line)
        self.tokens_to_parse = self.tokens_copy[1:-1]

        self.output_file = open(f'{parser_output}.xml', 'w')
        self.vm_writer = VMWriter(parser_output)

        self.current_token_arr: List[str] = self.tokens_to_parse[self.token_counter].split(' ')
        self.current_token: str = self.tokens_to_parse[self.token_counter]
        self.class_name: str = ''
        self.subroutine_void: bool = False
        self.if_label: int = 0
        self.while_label: int = 0
        self.is_constructor: bool = False
        self.function_type: str = ''
        self.subroutine_name: str = ''
        self.is_array: bool = False

        # Get symbol table and start compiling
        self.symbol_table = symbol_table
        self.symbol_table.class_start()
        self.compile_class()

        self.output_file.close()

    def compile_class(self) -> None:
        """Compile a complete class definition."""
        self.output_file.write('<class>\n')
        self.increase_indent()
        self.write_advance()  # 'class'
        self.class_name = str(self.current_token.split()[1])
        self.write_advance()  # className
        self.write_advance()  # '{'

        self.compile_class_var_dec()
        self.compile_subroutine()

        self.output_indent()
        self.output_file.write(self.current_token)
        self.output_file.write('</class>\n')

        # Recursion to compile multiple classes in one file
        token_count = len(self.tokens_to_parse)
        if self.token_counter + 1 != token_count:
            look_ahead = str(self.tokens_to_parse[self.token_counter + 1]).split()[1]
            if look_ahead == 'class':
                self.write_advance()
                self.compile_class()

    def compile_class_var_dec(self) -> None:
        """Compile class variable declarations (field/static)."""
        if (str(self.current_token) == '<keyword> field </keyword>\n' or
                str(self.current_token) == '<keyword> static </keyword>\n'):
            self.output_indent()
            self.output_file.write('<classVarDec>\n')
            self.increase_indent()

            class_var_kind = self.current_token.split()[1]
            class_var_type = self.tokens_to_parse[self.token_counter + 1].split()[1]
            every_two = 0
            start = 1

            while str(self.current_token) != '<symbol> ; </symbol>\n':
                if every_two % 2 == 0 and start > 2:
                    var_name = self.current_token.split()[1]
                    self.symbol_table.define(var_name, class_var_type, class_var_kind)
                self.write_advance()
                start += 1
                every_two += 1

            self.write_advance()  # ';'

            self.decrease_indent()
            self.output_indent()
            self.output_file.write('</classVarDec>\n')

        # Recursion: check if more, then call itself again
        if (str(self.current_token) == '<keyword> field </keyword>\n' or
                str(self.current_token) == '<keyword> static </keyword>\n'):
            self.compile_class_var_dec()

    def compile_subroutine(self) -> None:
        """Compile a subroutine declaration (constructor/function/method)."""
        self.output_indent()
        self.output_file.write('<subroutineDec>\n')
        self.increase_indent()

        self.function_type = str(self.current_token.split()[1])
        self.is_constructor = str(self.current_token.split()[1]) == 'constructor'

        self.write_advance()  # constructor|function|method
        self.subroutine_void = str(self.current_token.split()[1]) == 'void'

        self.write_advance()  # void|type
        self.subroutine_name = str(self.current_token.split()[1])
        self.write_advance()  # subroutineName
        self.write_advance()  # '('

        self.symbol_table.start_subroutine()
        self.compile_parameter_list()

        self.write_advance()  # ')' for end of parameter list

        self.output_indent()
        self.output_file.write('<subroutineBody>\n')
        self.increase_indent()
        self.write_advance()  # print the {

        # Compile all of the varDecs first
        if str(self.current_token) == '<keyword> var </keyword>\n':
            self.compile_var_dec()

        # VM code: write function declaration
        local_var_count = self.symbol_table.var_count('var')
        self.vm_writer.write_function(self.class_name, self.subroutine_name, local_var_count)

        # Code to set 'this' to point to passed object
        if self.is_constructor:
            self.vm_writer.write_push('constant', self.symbol_table.var_count('field'))
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        elif self.function_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)
            self.symbol_table.define_method('this', self.class_name, 'argument')

        # Enter statements (statements calls itself recursively)
        self.compile_statements()

        self.write_advance()  # } ending the subroutineBody
        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</subroutineBody>\n')
        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</subroutineDec>\n')

        # Track subroutines in symbol table
        self.symbol_table.define_subroutine_tracker(
            self.subroutine_name, 'method', self.class_name, self.subroutine_void
        )

        # Recursion: check if more subroutines
        if str(self.current_token) in (
            '<keyword> constructor </keyword>\n',
            '<keyword> function </keyword>\n',
            '<keyword> method </keyword>\n'
        ):
            self.compile_subroutine()

    def compile_parameter_list(self) -> None:
        """Compile a parameter list."""
        self.output_indent()
        self.output_file.write('<parameterList>\n')
        self.increase_indent()

        every_three = 0
        while str(self.current_token) != '<symbol> ) </symbol>\n':
            if every_three % 3 == 0:
                param_name = self.tokens_to_parse[self.token_counter + 1].split()[1]
                param_type = self.tokens_to_parse[self.token_counter].split()[1]
                self.symbol_table.define_method(param_name, param_type, 'argument')
            self.write_advance()
            every_three += 1

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</parameterList>\n')

    def compile_var_dec(self) -> None:
        """Compile variable declarations."""
        self.output_indent()
        self.output_file.write('<varDec>\n')
        self.increase_indent()

        self.write_advance()  # 'var'
        every_two = 0
        var_type = self.tokens_to_parse[self.token_counter].split()[1]
        self.write_advance()  # type

        while str(self.current_token) != '<symbol> ; </symbol>\n':
            if every_two % 2 == 0:
                var_name = self.tokens_to_parse[self.token_counter].split()[1]
                self.symbol_table.define_method(var_name, var_type, 'var')
            self.write_advance()
            every_two += 1

        self.write_advance()
        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</varDec>\n')

        if str(self.current_token) == '<keyword> var </keyword>\n':
            self.compile_var_dec()

    def compile_statements(self) -> None:
        """Compile a sequence of statements."""
        self.output_indent()
        self.output_file.write('<statements>\n')
        self.increase_indent()

        while self.check_statement():
            if str(self.current_token) == '<keyword> if </keyword>\n':
                self.compile_if()
            elif str(self.current_token) == '<keyword> let </keyword>\n':
                self.compile_let()
            elif str(self.current_token) == '<keyword> while </keyword>\n':
                self.compile_while()
            elif str(self.current_token) == '<keyword> do </keyword>\n':
                self.compile_do()
            elif str(self.current_token) == '<keyword> return </keyword>\n':
                self.compile_return()

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</statements>\n')

    def compile_do(self) -> None:
        """Compile a do statement."""
        self.output_indent()
        self.output_file.write('<doStatement>\n')
        self.increase_indent()

        self.write_advance()  # 'do'

        # LL(2) grammar: look ahead to see if ( or . for subroutine calls
        look_ahead = self.tokens_to_parse[self.token_counter + 1]

        if look_ahead == '<symbol> ( </symbol>\n':
            call_func = str(self.current_token.split()[1])
            self.vm_writer.write_push('pointer', '0')
            self.write_advance()  # subroutineName
            self.write_advance()  # '('
            self.compile_expression_list()
            self.write_advance()  # ')'
            self.write_advance()  # ';'
            num_args = self.symbol_table.get_id(call_func)
            self.vm_writer.write_call(f'{self.class_name}.{call_func}', num_args)
            if self.symbol_table.get_void(call_func):
                self.vm_writer.write_pop('temp', '0')
        else:
            other_class_name = str(self.current_token.split()[1])
            self.write_advance()  # className|varName
            self.write_advance()  # '.'
            call_func = str(self.current_token.split()[1])
            self.write_advance()  # subroutineName
            self.write_advance()  # '('
            self.compile_expression_list()
            self.write_advance()  # ')'
            self.write_advance()  # ';'
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
        self.output_indent()
        self.output_file.write('</doStatement>\n')

    def compile_let(self) -> None:
        """Compile a let statement."""
        self.output_indent()
        self.output_file.write('<letStatement>\n')
        self.increase_indent()

        self.write_advance()  # 'let'
        let_var_name = str(self.current_token.split()[1])
        self.write_advance()  # varName

        # Check if [] brackets are there
        if str(self.current_token) == '<symbol> [ </symbol>\n':
            self.is_array = True
            segment = self.symbol_table.get_kind(let_var_name)
            index = self.symbol_table.get_id(let_var_name)
            self.vm_writer.write_push(segment, index)
            self.write_advance()  # [
            self.compile_expression()
            self.write_advance()  # ]
            self.vm_writer.write_arithmetic('+')

        self.write_advance()  # '='
        self.compile_expression()
        self.write_advance()  # ';'

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
        self.output_indent()
        self.output_file.write('</letStatement>\n')

    def compile_while(self) -> None:
        """Compile a while statement."""
        self.output_indent()
        self.output_file.write('<whileStatement>\n')
        self.increase_indent()

        while_label_1 = f'whileL{self.while_label}'
        self.while_label += 1
        while_label_2 = f'whileL{self.while_label}'
        self.while_label += 1
        self.vm_writer.write_label(while_label_1)

        self.write_advance()  # 'while'
        self.write_advance()  # (
        self.compile_expression()

        self.vm_writer.write_arithmetic('NOT')
        self.vm_writer.write_if(while_label_2)

        self.write_advance()  # )
        self.write_advance()  # {
        self.compile_statements()
        self.write_advance()  # }

        self.vm_writer.write_goto(while_label_1)
        self.vm_writer.write_label(while_label_2)

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</whileStatement>\n')

    def compile_return(self) -> None:
        """Compile a return statement."""
        self.output_indent()
        self.output_file.write('<returnStatement>\n')
        self.increase_indent()

        self.write_advance()  # return

        # If expression, compile that as well
        if self.check_more_terms():
            self.compile_expression()
        self.write_advance()  # ;

        # If void push 0, if not return top of stack
        if self.subroutine_void:
            self.vm_writer.write_push('constant', 0)
        self.vm_writer.write_return()

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</returnStatement>\n')

    def compile_if(self) -> None:
        """Compile an if statement."""
        self.output_indent()
        self.output_file.write('<ifStatement>\n')
        self.increase_indent()

        self.write_advance()  # 'if'
        self.write_advance()  # '('
        self.compile_expression()
        self.write_advance()  # ')'

        self.vm_writer.write_arithmetic('NOT')
        if_label_1 = f'ifL{self.if_label}'
        self.if_label += 1
        self.vm_writer.write_if(if_label_1)

        self.write_advance()  # '{'
        self.compile_statements()

        if_label_2 = f'ifL{self.if_label}'
        self.if_label += 1
        self.vm_writer.write_goto(if_label_2)

        self.vm_writer.write_label(if_label_1)
        self.write_advance()  # '}'

        # Check if else statement is there
        if str(self.current_token) == '<keyword> else </keyword>\n':
            self.write_advance()  # 'else'
            self.write_advance()  # '{'
            self.compile_statements()
            self.write_advance()  # '}'

        self.vm_writer.write_label(if_label_2)

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</ifStatement>\n')

    def compile_expression(self) -> None:
        """Compile an expression."""
        self.output_indent()
        self.output_file.write('<expression>\n')
        self.increase_indent()

        self.compile_term()

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</expression>\n')

    def compile_term(self) -> None:
        """Compile a term."""
        self.output_indent()
        self.output_file.write('<term>\n')
        self.increase_indent()

        token_tag = str(self.current_token.split()[0])
        vm_token = str(self.current_token.split()[1])

        if token_tag == '<identifier>':
            look_ahead = self.tokens_to_parse[self.token_counter + 1]

            if look_ahead == '<symbol> [ </symbol>\n':
                # Array access
                segment = self.symbol_table.get_kind(vm_token)
                index = self.symbol_table.get_id(vm_token)
                self.vm_writer.write_push(segment, index)
                self.write_advance()  # varName
                self.write_advance()  # [
                self.compile_expression()
                self.write_advance()  # ]
                self.vm_writer.write_arithmetic('+')
                self.vm_writer.write_pop('pointer', '1')
                self.vm_writer.write_push('that', '0')

            elif look_ahead == '<symbol> ( </symbol>\n':
                # Subroutine call
                call_func = str(self.current_token.split()[1])
                self.vm_writer.write_push('argument', '0')
                self.write_advance()  # subroutineName
                self.write_advance()  # '('
                self.compile_expression_list()
                self.write_advance()  # ')'
                num_args = self.symbol_table.get_id(call_func)
                self.vm_writer.write_call(f'{self.class_name}.{call_func}', num_args)
                if self.symbol_table.get_void(call_func):
                    self.vm_writer.write_pop('temp', '0')

            elif look_ahead == '<symbol> . </symbol>\n':
                # Call to another class
                other_class_name = str(self.current_token.split()[1])
                self.write_advance()  # className|varName
                self.write_advance()  # '.'
                call_func = str(self.current_token.split()[1])
                self.write_advance()  # subroutineName
                self.write_advance()  # '('
                self.compile_expression_list()
                self.write_advance()  # ')'
                num_args = self.symbol_table.get_id(call_func)
                self.vm_writer.write_call(f'{other_class_name}.{call_func}', num_args)

            else:
                # varName
                segment = self.symbol_table.get_kind(vm_token)
                index = self.symbol_table.get_id(vm_token)
                self.vm_writer.write_push(segment, index)
                self.write_advance()

        elif token_tag == '<integerConstant>':
            self.vm_writer.write_push('constant', vm_token)
            self.write_advance()

        elif token_tag == '<stringConstant>':
            array_vm_token = self.current_token.split()
            each_letter = list(' '.join(array_vm_token[1:-1]))
            self.vm_writer.write_push('constant', len(each_letter))
            self.vm_writer.write_call('String.new', 1)
            for letter in each_letter:
                self.vm_writer.write_push('constant', ord(letter))
                self.vm_writer.write_call('String.appendChar', 2)
            self.write_advance()

        elif str(self.current_token) == '<keyword> true </keyword>\n':
            self.vm_writer.write_push('constant', 1)
            self.vm_writer.write_arithmetic('NEG')
            self.write_advance()

        elif str(self.current_token) == '<keyword> false </keyword>\n':
            self.vm_writer.write_push('constant', 0)
            self.write_advance()

        elif str(self.current_token) == '<keyword> null </keyword>\n':
            self.vm_writer.write_push('constant', 0)
            self.write_advance()

        elif str(self.current_token) == '<keyword> this </keyword>\n':
            self.vm_writer.write_push('pointer', 0)
            self.write_advance()

        elif str(self.current_token) == '<symbol> ( </symbol>\n':
            self.write_advance()  # (
            self.compile_expression()
            self.write_advance()  # )

        elif str(self.current_token) == '<symbol> - </symbol>\n':
            self.write_advance()
            self.compile_term()
            self.vm_writer.write_arithmetic('NEG')

        elif str(self.current_token) == '<symbol> ~ </symbol>\n':
            self.write_advance()
            self.compile_term()
            self.vm_writer.write_arithmetic('~')

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</term>\n')

        # Check for operator and use recursion
        if self.check_op():
            op_term = str(self.current_token.split()[1])
            self.write_advance()  # op
            self.compile_term()
            self.vm_writer.write_arithmetic(op_term)

    def compile_expression_list(self) -> None:
        """Compile a comma-separated list of expressions."""
        self.output_indent()
        self.output_file.write('<expressionList>\n')
        self.increase_indent()

        while self.check_more_terms():
            self.compile_expression()
            if str(self.current_token) == '<symbol> , </symbol>\n':
                self.write_advance()  # ','

        self.decrease_indent()
        self.output_indent()
        self.output_file.write('</expressionList>\n')

    def output_indent(self) -> None:
        """Write the current indentation to the output file."""
        for _ in range(self.indent):
            self.output_file.write('  ')

    def advance(self) -> None:
        """Advance to the next token."""
        self.token_counter += 1
        self.current_token = self.tokens_to_parse[self.token_counter]

    def write_advance(self) -> None:
        """Write the current token and advance to the next."""
        self.output_indent()
        self.output_file.write(self.current_token)
        self.advance()

    def increase_indent(self) -> None:
        """Increase the indentation level."""
        self.indent += 1

    def decrease_indent(self) -> None:
        """Decrease the indentation level."""
        self.indent -= 1

    def check_statement(self) -> bool:
        """Check if the current token is a statement keyword."""
        return str(self.current_token) in STATEMENT_TOKENS

    def check_op(self) -> bool:
        """Check if the current token is an operator."""
        return str(self.current_token) in OPERATOR_TOKENS

    def check_more_terms(self) -> bool:
        """Check if the current token can start a term."""
        token_tag = str(self.current_token.split()[0])

        if token_tag in ('<identifier>', '<integerConstant>', '<stringConstant>'):
            return True

        term_keywords = [
            '<keyword> true </keyword>\n',
            '<keyword> false </keyword>\n',
            '<keyword> null </keyword>\n',
            '<keyword> this </keyword>\n'
        ]
        if str(self.current_token) in term_keywords:
            return True

        term_symbols = [
            '<symbol> ( </symbol>\n',
            '<symbol> - </symbol>\n',
            '<symbol> ~ </symbol>\n'
        ]
        if str(self.current_token) in term_symbols:
            return True

        return False

    
