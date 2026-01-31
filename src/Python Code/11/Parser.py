"""
Jack Parser - Recursive descent parser and code generator.

Parses tokenized Jack source code and generates VM code.
Part of the Nand2Tetris course (Project 11).
"""

from typing import List, Optional
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class Parser:
    """Recursive descent parser and code generator for Jack language."""

    # Token constants
    FIELD_TOKEN = '<keyword> field </keyword>\n'
    STATIC_TOKEN = '<keyword> static </keyword>\n'
    VAR_TOKEN = '<keyword> var </keyword>\n'
    CONSTRUCTOR_TOKEN = '<keyword> constructor </keyword>\n'
    FUNCTION_TOKEN = '<keyword> function </keyword>\n'
    METHOD_TOKEN = '<keyword> method </keyword>\n'
    VOID_TOKEN = '<keyword> void </keyword>\n'
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
    EQUALS_TOKEN = '<symbol> = </symbol>\n'

    def __init__(self, parser_input: str, parser_output: str, symbol_table: SymbolTable) -> None:
        """Initialize the parser."""
        self.tokens: List[str] = []
        self.token_counter = 0
        self.indent = 0

        with open(parser_input) as f:
            tokens_copy = f.readlines()
        self.tokens = tokens_copy[1:-1]

        self.output = open(f"{parser_output}.xml", 'w')
        self.vm_writer = VMWriter(parser_output)
        
        self.current_token = self.tokens[self.token_counter]
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
        self._compile_class()

        self.output.close()

    def _get_token_value(self) -> str:
        """Extract the value from the current token."""
        return str(self.current_token.split()[1])

    def _compile_class(self) -> None:
        """Compile a complete class."""
        self.output.write('<class>\n')
        self._increase_indent()
        self._write_and_advance()  # 'class'
        self.class_name = self._get_token_value()
        self._write_and_advance()  # className
        self._write_and_advance()  # '{'

        self._compile_class_var_dec()
        self._compile_subroutine()
        
        self._write_indent()
        self.output.write(self.current_token)
        self.output.write('</class>\n')

        # Handle multiple classes in one file
        if self.token_counter + 1 < len(self.tokens):
            look_ahead = str(self.tokens[self.token_counter + 1]).split()[1]
            if look_ahead == 'class':
                self._write_and_advance()
                self._compile_class()

    def _compile_class_var_dec(self) -> None:
        """Compile class variable declarations."""
        if str(self.current_token) in [self.FIELD_TOKEN, self.STATIC_TOKEN]:
            self._write_indent()
            self.output.write('<classVarDec>\n')
            self._increase_indent()
            
            var_kind = self._get_token_value()
            var_type = self.tokens[self.token_counter + 1].split()[1]
            counter = 0
            start = 1
            
            while str(self.current_token) != self.SEMICOLON_TOKEN:
                if counter % 2 == 0 and start > 2:
                    var_name = self._get_token_value()
                    self.symbol_table.define(var_name, var_type, var_kind)
                self._write_and_advance()
                start += 1
                counter += 1
            
            self._write_and_advance()  # ';'
            self._decrease_indent()
            self._write_indent()
            self.output.write('</classVarDec>\n')

            if str(self.current_token) in [self.FIELD_TOKEN, self.STATIC_TOKEN]:
                self._compile_class_var_dec()

    def _compile_subroutine(self) -> None:
        """Compile a subroutine."""
        self._write_indent()
        self.output.write('<subroutineDec>\n')
        self._increase_indent()
        
        self.function_type = self._get_token_value()
        self.is_constructor = (self.function_type == 'constructor')
        self._write_and_advance()  # constructor|function|method
        
        self.subroutine_is_void = (self._get_token_value() == 'void')
        self._write_and_advance()  # void|type
        
        self.subroutine_name = self._get_token_value()
        self._write_and_advance()  # subroutineName
        self._write_and_advance()  # '('
        
        self.symbol_table.startSubroutine()
        if self.function_type == 'method':
            self.symbol_table.defineMethod('this', self.class_name, 'argument')

        self._compile_parameter_list()
        self._write_and_advance()  # ')'

        self._write_indent()
        self.output.write('<subroutineBody>\n')
        self._increase_indent()
        self._write_and_advance()  # '{'

        if str(self.current_token) == self.VAR_TOKEN:
            self._compile_var_dec()
        
        # Write function declaration in VM code
        num_locals = self.symbol_table.varCount('var')
        self.vm_writer.writeFunction(self.class_name, self.subroutine_name, num_locals)
        
        # Handle constructor and method setup
        if self.is_constructor:
            self.vm_writer.writePush('constant', self.symbol_table.varCount('field'))
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('pointer', 0)
        elif self.function_type == 'method':
            self.vm_writer.writePush('argument', 0)
            self.vm_writer.writePop('pointer', 0)

        self._compile_statements()
        self._write_and_advance()  # '}'
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineBody>\n')
        self._decrease_indent()
        self._write_indent()
        self.output.write('</subroutineDec>\n')
        
        self.symbol_table.defineSubroutineTracker(
            self.subroutine_name, 'method', self.class_name, self.subroutine_is_void
        )

        if str(self.current_token) in [self.CONSTRUCTOR_TOKEN, self.FUNCTION_TOKEN, self.METHOD_TOKEN]:
            self._compile_subroutine()

    def _compile_parameter_list(self) -> None:
        """Compile a parameter list."""
        self._write_indent()
        self.output.write('<parameterList>\n')
        self._increase_indent()
        
        counter = 0
        while str(self.current_token) != self.RPAREN_TOKEN:
            if counter % 3 == 0:
                param_name = self.tokens[self.token_counter + 1].split()[1]
                param_type = self._get_token_value()
                self.symbol_table.defineMethod(param_name, param_type, 'argument')
            self._write_and_advance()
            counter += 1
        
        self._decrease_indent()
        self._write_indent()
        self.output.write('</parameterList>\n')

    def _compile_var_dec(self) -> None:
        """Compile variable declarations."""
        self._write_indent()
        self.output.write('<varDec>\n')
        self._increase_indent()
        
        self._write_and_advance()  # 'var'
        var_type = self._get_token_value()
        self._write_and_advance()  # type
        
        counter = 0
        while str(self.current_token) != self.SEMICOLON_TOKEN:
            if counter % 2 == 0:
                var_name = self._get_token_value()
                self.symbol_table.defineMethod(var_name, var_type, 'var')
            self._write_and_advance()
            counter += 1
        
        self._write_and_advance()  # ';'
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
        
        look_ahead = self.tokens[self.token_counter + 1]
        if look_ahead == self.LPAREN_TOKEN:
            call_name = self._get_token_value()
            self.vm_writer.writePush('pointer', '0')
            self._write_and_advance()  # subroutineName
            self._write_and_advance()  # '('
            self._compile_expression_list()
            self._write_and_advance()  # ')'
            self._write_and_advance()  # ';'
            
            num_args = self.symbol_table.getIDofClass(call_name, self.class_name)
            self.vm_writer.writeCall(f"{self.class_name}.{call_name}", str(num_args))
            if self.symbol_table.getVoid(call_name, self.class_name):
                self.vm_writer.writePop('temp', '0')
        else:
            other_class_name = self._get_token_value()
            self._write_and_advance()  # className|varName
            self._write_and_advance()  # '.'
            call_name = self._get_token_value()
            
            if self.symbol_table.getKind(other_class_name) is not None:
                segment = self.symbol_table.getKind(other_class_name)
                index = self.symbol_table.getID(other_class_name)
                self.vm_writer.writePush(segment, index)
            
            self._write_and_advance()  # subroutineName
            self._write_and_advance()  # '('
            self._compile_expression_list()
            self._write_and_advance()  # ')'
            self._write_and_advance()  # ';'
            
            self._write_call_for_do(other_class_name, call_name)

        self._decrease_indent()
        self._write_indent()
        self.output.write('</doStatement>\n')

    def _write_call_for_do(self, other_class_name: str, call_name: str) -> None:
        """Write the VM call instruction for a do statement."""
        if self.symbol_table.getKind(other_class_name) is None:
            num_args = self.symbol_table.getIDofClass(call_name, other_class_name)
            self.vm_writer.writeCall(f"{other_class_name}.{call_name}", str(num_args))
            if self.symbol_table.getVoid(call_name, other_class_name):
                self.vm_writer.writePop('temp', '0')
        else:
            real_class_name = self.symbol_table.getType(other_class_name)
            if real_class_name is not None:
                num_args = self.symbol_table.getIDofClass(call_name, real_class_name)
                self.vm_writer.writeCall(f"{real_class_name}.{call_name}", str(num_args))
                if self.symbol_table.getVoid(call_name, real_class_name):
                    self.vm_writer.writePop('temp', '0')
            else:
                num_args = self.symbol_table.getIDofClass(call_name, other_class_name)
                self.vm_writer.writeCall(f"{other_class_name}.{call_name}", str(num_args))
                if self.symbol_table.getVoid(call_name, other_class_name):
                    self.vm_writer.writePop('temp', '0')

    def _compile_let(self) -> None:
        """Compile a let statement."""
        self._write_indent()
        self.output.write('<letStatement>\n')
        self._increase_indent()

        self._write_and_advance()  # 'let'
        var_name = self._get_token_value()
        self._write_and_advance()  # varName
        
        if str(self.current_token) == self.LBRACKET_TOKEN:
            self.is_array = True
            segment = self.symbol_table.getKind(var_name)
            index = self.symbol_table.getID(var_name)
            self.vm_writer.writePush(segment, index)
            self._write_and_advance()  # '['
            self._compile_expression()
            self._write_and_advance()  # ']'
            self.vm_writer.writeArithmetic('+')
        
        self._write_and_advance()  # '='
        self._compile_expression()
        self._write_and_advance()  # ';'
        
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

        label1 = f"whileL{self.while_label_counter}"
        self.while_label_counter += 1
        label2 = f"whileL{self.while_label_counter}"
        self.while_label_counter += 1
        
        self.vm_writer.writeLabel(label1)
        self._write_and_advance()  # 'while'
        self._write_and_advance()  # '('
        self._compile_expression()
        
        self.vm_writer.writeArithmetic('NOT')
        self.vm_writer.writeIf(label2)
        
        self._write_and_advance()  # ')'
        self._write_and_advance()  # '{'
        self._compile_statements()
        self._write_and_advance()  # '}'
        
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

        self._write_and_advance()  # 'return'
        
        if self._check_more_terms():
            self._compile_expression()
        
        self._write_and_advance()  # ';'
        
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

        self._write_and_advance()  # 'if'
        self._write_and_advance()  # '('
        self._compile_expression()
        self._write_and_advance()  # ')'

        self.vm_writer.writeArithmetic('NOT')
        label1 = f"ifL{self.if_label_counter}"
        self.if_label_counter += 1
        self.vm_writer.writeIf(label1)

        self._write_and_advance()  # '{'
        self._compile_statements()

        label2 = f"ifL{self.if_label_counter}"
        self.if_label_counter += 1
        self.vm_writer.writeGoto(label2)
        self.vm_writer.writeLabel(label1)

        self._write_and_advance()  # '}'
        
        if str(self.current_token) == self.ELSE_TOKEN:
            self._write_and_advance()  # 'else'
            self._write_and_advance()  # '{'
            self._compile_statements()
            self._write_and_advance()  # '}'
        
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

        token_type = str(self.current_token.split()[0])
        vm_token = self._get_token_value()

        if token_type == '<identifier>':
            self._compile_identifier_term(vm_token)
        elif token_type == '<integerConstant>':
            self.vm_writer.writePush('constant', vm_token)
            self._write_and_advance()
        elif token_type == '<stringConstant>':
            self._compile_string_constant()
        elif str(self.current_token) == self.TRUE_TOKEN:
            self.vm_writer.writePush('constant', 1)
            self.vm_writer.writeArithmetic('NEG')
            self._write_and_advance()
        elif str(self.current_token) == self.FALSE_TOKEN:
            self.vm_writer.writePush('constant', 0)
            self._write_and_advance()
        elif str(self.current_token) == self.NULL_TOKEN:
            self.vm_writer.writePush('constant', 0)
            self._write_and_advance()
        elif str(self.current_token) == self.THIS_TOKEN:
            self.vm_writer.writePush('pointer', 0)
            self._write_and_advance()
        elif str(self.current_token) == self.LPAREN_TOKEN:
            self._write_and_advance()  # '('
            self._compile_expression()
            self._write_and_advance()  # ')'
        elif str(self.current_token) == self.MINUS_TOKEN:
            self._write_and_advance()
            self._compile_term()
            self.vm_writer.writeArithmetic('NEG')
        elif str(self.current_token) == self.TILDE_TOKEN:
            self._write_and_advance()
            self._compile_term()
            self.vm_writer.writeArithmetic('~')

        self._decrease_indent()
        self._write_indent()
        self.output.write('</term>\n')

        if self._check_op():
            op = self._get_token_value()
            self._write_and_advance()
            self._compile_term()
            self.vm_writer.writeArithmetic(op)

    def _compile_identifier_term(self, vm_token: str) -> None:
        """Compile an identifier-based term."""
        look_ahead = self.tokens[self.token_counter + 1]
        
        if look_ahead == self.LBRACKET_TOKEN:
            # Array access
            segment = self.symbol_table.getKind(vm_token)
            index = self.symbol_table.getID(vm_token)
            self.vm_writer.writePush(segment, index)
            self._write_and_advance()  # varName
            self._write_and_advance()  # '['
            self._compile_expression()
            self._write_and_advance()  # ']'
            self.vm_writer.writeArithmetic('+')
            self.vm_writer.writePop('pointer', '1')
            self.vm_writer.writePush('that', '0')
        elif look_ahead == self.LPAREN_TOKEN:
            # Function call
            call_name = vm_token
            self.vm_writer.writePush('argument', '0')
            self._write_and_advance()
            self._write_and_advance()  # '('
            self._compile_expression_list()
            self._write_and_advance()  # ')'
            num_args = self.symbol_table.getIDofClass(call_name, self.class_name)
            self.vm_writer.writeCall(f"{self.class_name}.{call_name}", str(num_args))
            if self.symbol_table.getVoid(call_name, self.class_name):
                self.vm_writer.writePop('temp', '0')
        elif look_ahead == self.DOT_TOKEN:
            # Method call
            other_class = vm_token
            self._write_and_advance()  # className|varName
            self._write_and_advance()  # '.'
            call_name = self._get_token_value()
            self._write_and_advance()  # subroutineName
            self._write_and_advance()  # '('
            self._compile_expression_list()
            self._write_and_advance()  # ')'
            
            real_class = self.symbol_table.getType(other_class)
            if self.symbol_table.getID(other_class) is not None:
                self.vm_writer.writePush(
                    self.symbol_table.getKind(other_class),
                    self.symbol_table.getID(other_class)
                )
            
            if real_class is not None:
                num_args = self.symbol_table.getIDofClass(call_name, real_class)
                self.vm_writer.writeCall(f"{real_class}.{call_name}", str(num_args))
                if self.symbol_table.getVoid(call_name, real_class):
                    self.vm_writer.writePop('temp', '0')
            else:
                num_args = self.symbol_table.getIDofClass(call_name, other_class)
                self.vm_writer.writeCall(f"{other_class}.{call_name}", str(num_args))
                if self.symbol_table.getVoid(call_name, other_class):
                    self.vm_writer.writePop('temp', '0')
        else:
            # Simple variable
            segment = self.symbol_table.getKind(vm_token)
            index = self.symbol_table.getID(vm_token)
            self.vm_writer.writePush(segment, index)
            self._write_and_advance()

    def _compile_string_constant(self) -> None:
        """Compile a string constant."""
        token_parts = self.current_token.split()
        chars = list(' '.join(token_parts[1:-1]))
        self.vm_writer.writePush('constant', len(chars))
        self.vm_writer.writeCall('String.new', 1)
        for char in chars:
            self.vm_writer.writePush('constant', ord(char))
            self.vm_writer.writeCall('String.appendChar', 2)
        self._write_and_advance()

    def _compile_expression_list(self) -> None:
        """Compile an expression list."""
        self._write_indent()
        self.output.write('<expressionList>\n')
        self._increase_indent()
        
        while self._check_more_terms():
            self._compile_expression()
            if str(self.current_token) == self.COMMA_TOKEN:
                self._write_and_advance()

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
        return str(self.current_token) in [
            self.IF_TOKEN, self.LET_TOKEN, self.WHILE_TOKEN,
            self.DO_TOKEN, self.RETURN_TOKEN
        ]

    def _check_op(self) -> bool:
        """Check if current token is an operator."""
        op_tokens = [
            '<symbol> + </symbol>\n', '<symbol> - </symbol>\n',
            '<symbol> * </symbol>\n', '<symbol> / </symbol>\n',
            '<symbol> &amp; </symbol>\n', '<symbol> | </symbol>\n',
            '<symbol> &lt; </symbol>\n', '<symbol> &gt; </symbol>\n',
            '<symbol> = </symbol>\n', '<symbol> ^ </symbol>\n'
        ]
        return str(self.current_token) in op_tokens

    def _check_more_terms(self) -> bool:
        """Check if current token can start a term."""
        token_type = str(self.current_token.split()[0])
        
        if token_type in ['<identifier>', '<integerConstant>', '<stringConstant>']:
            return True
        
        return str(self.current_token) in [
            self.TRUE_TOKEN, self.FALSE_TOKEN, self.NULL_TOKEN,
            self.THIS_TOKEN, self.LPAREN_TOKEN, self.MINUS_TOKEN,
            self.TILDE_TOKEN
        ]
