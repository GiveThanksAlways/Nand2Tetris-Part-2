"""
Main module for the Jack compiler.

This module orchestrates the compilation process, walking through directories
to find .jack files, tokenizing them, and then parsing them to generate
XML and VM output.
"""

import os
from typing import List

from Parser import Parser
from SymbolTable import SymbolTable
from Tokenizer import inside_a_string, token_type, token_wrap

# Non-terminal symbols in the Jack grammar
NON_TERMINALS: List[str] = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList', 'subroutineBody',
    'varDec', 'statements', 'whileStatement', 'ifStatement', 'returnStatement',
    'letStatement', 'doStatement', 'expression', 'term', 'expressionList'
]


def initialize_symbol_table() -> SymbolTable:
    """
    Initialize the symbol table with OS function definitions.

    Returns:
        A SymbolTable with predefined OS functions.
    """
    symbol_table = SymbolTable()

    # Define OS functions with their argument counts and void status
    symbol_table.define_subroutine_tracker('deAlloc', '1', 'OS', True)
    symbol_table.define_subroutine_tracker('keyPressed', '0', 'OS', False)
    symbol_table.define_subroutine_tracker('wait', '1', 'OS', True)
    symbol_table.define('new', '1', 'OS')
    symbol_table.define_subroutine_tracker('setColor', '1', 'OS', True)
    symbol_table.define_subroutine_tracker('drawRectangle', '4', 'OS', True)
    symbol_table.define_subroutine_tracker('printInt', '1', 'OS', True)
    symbol_table.define_subroutine_tracker('printString', '1', 'OS', True)
    symbol_table.define_subroutine_tracker('readInt', '1', 'OS', True)

    return symbol_table


def remove_comments(line: str) -> str:
    """
    Remove single-line and multi-line comments from a line.

    Args:
        line: The source line to process.

    Returns:
        The line with comments removed.
    """
    line = line.split('//', 1)[0]
    line = line.split('/*')[0]
    line = line.rstrip()

    char_list = list(line)
    if len(char_list) > 2:
        if char_list[0] == ' ' and char_list[1] == '*':
            line = line.split('*')[0]
            line = line.rstrip()

    return line


def tokenize_content(content: List[str]) -> List[str]:
    """
    Tokenize the content of a Jack source file.

    Args:
        content: List of source code lines.

    Returns:
        List of tokens.
    """
    token_array: List[str] = []
    tokens_to_print: List[str] = []
    string_counter = 0

    for item in content:
        for letter in item:
            if letter == '"':
                string_counter += 1

            if inside_a_string(string_counter):
                token_array.append(letter)
            elif letter != ' ':
                if token_type(letter) == 'symbol':
                    tokens_to_print.append(''.join(token_array))
                    token_array = []
                    token_array.append(letter)
                    tokens_to_print.append(''.join(token_array))
                    token_array = []
                else:
                    token_array.append(letter)
            else:
                tokens_to_print.append(''.join(token_array))
                token_array = []

    tokens_to_print = [x.strip() for x in tokens_to_print]
    tokens_to_print = [item for item in tokens_to_print if item != '']

    return tokens_to_print


def process_jack_file(
    folder_name: str,
    filename: str,
    symbol_table: SymbolTable
) -> None:
    """
    Process a single Jack source file.

    Args:
        folder_name: The directory containing the file.
        filename: The Jack source filename.
        symbol_table: The symbol table to use for compilation.
    """
    content: List[str] = []
    file_path = os.path.join(folder_name, filename)

    with open(file_path) as f:
        for line in f:
            processed_line = remove_comments(line)
            content.append(processed_line)

    content = [x.strip() for x in content]
    content = [item for item in content if item != '']

    output_string = os.path.join(folder_name, filename[:filename.index('.')])
    token_output_filename = f"{filename[:filename.index('.')]}Token.xml"
    token_output_path = os.path.join(folder_name, token_output_filename)

    tokens_to_print = tokenize_content(content)

    xml_tokens_list: List[str] = ['<tokens>']
    for token in tokens_to_print:
        token_wrap(xml_tokens_list, token)
    xml_tokens_list.append('</tokens>')

    with open(token_output_path, 'w') as output:
        for item in xml_tokens_list:
            output.write(item)
            output.write('\n')

    Parser(token_output_path, output_string, symbol_table)


def main() -> None:
    """Main entry point for the Jack compiler."""
    symbol_table = initialize_symbol_table()

    for folder_name, subfolders, filenames in os.walk('/home/runner'):
        for filename in filenames:
            if filename.split('.')[-1] == 'jack':
                process_jack_file(folder_name, filename, symbol_table)


if __name__ == '__main__':
    main()
