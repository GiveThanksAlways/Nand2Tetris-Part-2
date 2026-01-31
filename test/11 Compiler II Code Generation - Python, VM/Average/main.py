"""
Main module for the Jack compiler.

This module serves as the entry point for the Jack compiler, orchestrating
the tokenization and parsing of Jack source files to generate VM code.
"""

import os
from typing import List

from Parser import Parser
from SymbolTable import SymbolTable
from Tokenizer import inside_a_string, token_type, token_wrap

# Non-terminal symbols in the Jack grammar
NON_TERMINALS: List[str] = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList',
    'subroutineBody', 'varDec', 'statements', 'whileStatement',
    'ifStatement', 'returnStatement', 'letStatement', 'doStatement',
    'expression', 'term', 'expressionList'
]


def initialize_symbol_table() -> SymbolTable:
    """
    Initialize the symbol table with OS library function definitions.

    Returns:
        A SymbolTable populated with standard OS library functions.
    """
    symbol_table = SymbolTable()

    # OS library functions
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


def process_jack_file(
    file_path: str,
    folder_name: str,
    filename: str,
    symbol_table: SymbolTable
) -> None:
    """
    Process a single Jack file through tokenization and parsing.

    Args:
        file_path: Full path to the Jack file.
        folder_name: Directory containing the file.
        filename: Name of the Jack file.
        symbol_table: The symbol table to use for compilation.
    """
    content: List[str] = []

    # Read and preprocess the file
    with open(file_path) as f:
        for line in f:
            # Remove // and /* comments
            line = line.split('//', 1)[0]
            line = line.split('/*')[0]
            line = line.rstrip()

            # Remove multi-line comments starting with *
            chars = list(line)
            if len(chars) > 2:
                if chars[0] == ' ' and chars[1] == '*':
                    line = line.split('*')[0]
                    line = line.rstrip()
            content.append(line)

    # Clean up content
    content = [x.strip() for x in content]
    content = [item for item in content if item != '']

    # Set up output paths
    output_string = os.path.join(folder_name, filename[:filename.index('.')])
    output_token_string = f"{filename[:filename.index('.')]}Token.xml"
    output = open(os.path.join(folder_name, output_token_string), 'w')

    # Tokenize the content
    token_array: List[str] = []
    tokens_to_print: List[str] = []
    string_counter = 0

    for item in content:
        for letter in item:
            # Track string boundaries using quote count
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

    # Clean up tokens
    tokens_to_print = [x.strip() for x in tokens_to_print]
    tokens_to_print = [item for item in tokens_to_print if item != '']

    # Wrap tokens in XML
    xml_tokens_list: List[str] = ['<tokens>']
    for token in tokens_to_print:
        token_wrap(xml_tokens_list, token)
    xml_tokens_list.append('</tokens>')

    # Write XML tokens to output file
    for item in xml_tokens_list:
        output.write(item)
        output.write('\n')
    output.close()
    xml_tokens_list.clear()

    # Parse the tokens
    Parser(os.path.join(folder_name, output_token_string), output_string, symbol_table)


def main() -> None:
    """Main entry point for the Jack compiler."""
    symbol_table = initialize_symbol_table()

    for folder_name, subfolders, filenames in os.walk('/home/runner'):
        for filename in filenames:
            if filename.split('.')[-1] == 'jack':
                file_path = os.path.join(folder_name, filename)
                process_jack_file(file_path, folder_name, filename, symbol_table)


if __name__ == '__main__':
    main()
