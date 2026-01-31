#!/usr/bin/env python3
"""
Jack Compiler - Main entry point.

This module compiles Jack source files (.jack) into VM bytecode (.vm).
It handles both single files and directories containing Jack files.
"""

import glob
import os
import sys
from pathlib import Path
from typing import List

from Parser import Parser
from SymbolTable import SymbolTable
from Tokenizer import inside_a_string, token_type, token_wrap

# Non-terminal elements in the Jack grammar
NON_TERMINALS: List[str] = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList', 'subroutineBody',
    'varDec', 'statements', 'whileStatement', 'ifStatement', 'returnStatement',
    'letStatement', 'doStatement', 'expression', 'term', 'expressionList'
]


def read_and_clean_file(file_path: str) -> List[str]:
    """
    Read a Jack source file and remove comments.

    Args:
        file_path: Path to the Jack source file.

    Returns:
        List of cleaned source code lines.
    """
    content = []
    with open(file_path) as f:
        for line in f:
            line = line.lstrip(' ')
            if not line.startswith(("//", "/**", "*", "*/")):
                line = line.split('//', 1)[0]
                line = line.rstrip()
                content.append(line)

    content = [x.strip() for x in content]
    content = [item for item in content if item != '']
    return content


def tokenize_content(content: List[str]) -> List[str]:
    """
    Convert source lines into a list of tokens.

    Args:
        content: List of cleaned source code lines.

    Returns:
        List of token strings.
    """
    token_array = []
    tokens_to_print = []
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


def write_xml_tokens(tokens: List[str], output_path: str) -> None:
    """
    Wrap tokens in XML and write to file.

    Args:
        tokens: List of token strings.
        output_path: Path to the output XML file.
    """
    xml_tokens_list = ['<tokens>']
    for token in tokens:
        token_wrap(xml_tokens_list, token)
    xml_tokens_list.append('</tokens>')

    with open(output_path, 'w') as output:
        for item in xml_tokens_list:
            output.write(item)
            output.write('\n')


def process_jack_file(filename: str, folder_name: str,
                       symbol_table: SymbolTable) -> None:
    """
    Process a single Jack file through tokenization and parsing.

    Args:
        filename: Name of the Jack file.
        folder_name: Directory containing the file.
        symbol_table: The symbol table for compilation.
    """
    file_path = os.path.join(folder_name, filename)
    content = read_and_clean_file(file_path)
    tokens = tokenize_content(content)

    base_name = filename[:filename.index('.')]
    output_string = os.path.join(folder_name, base_name)
    token_xml_path = os.path.join(folder_name, f'{base_name}Token.xml')

    write_xml_tokens(tokens, token_xml_path)
    Parser(token_xml_path, output_string, symbol_table)


def compile_directory(directory: str, symbol_table: SymbolTable) -> None:
    """
    Compile all Jack files in a directory.

    Args:
        directory: Path to the directory.
        symbol_table: The symbol table for compilation.
    """
    for folder_name, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.jack'):
                process_jack_file(filename, folder_name, symbol_table)


def compile_os_classes(symbol_table: SymbolTable) -> None:
    """
    Compile the OS class library to populate symbol table.

    Args:
        symbol_table: The symbol table for compilation.
    """
    os_dir = "OS"
    os_folder = str(Path(os_dir).resolve())
    original_dir = os.getcwd()
    os.chdir(os.path.realpath(os_dir))

    items = os.listdir(".")
    os_files = [item for item in items if item.endswith(".jack")]

    for filename in os_files:
        file_path = os.path.join(os.getcwd(), filename)
        content = read_and_clean_file(file_path)
        tokens = tokenize_content(content)

        base_name = filename[:filename.index('.')]
        output_string = os.path.join(os_folder, base_name)
        token_xml_path = os.path.join(os_folder, f'{base_name}Token.xml')

        write_xml_tokens(tokens, token_xml_path)
        Parser(token_xml_path, output_string, symbol_table)

    os.chdir(original_dir)


def main() -> None:
    """Main entry point for the Jack compiler."""
    if len(sys.argv) < 2:
        print("Usage: python JackCompiler.py <file.jack | directory>")
        sys.exit(1)

    symbol_table = SymbolTable()

    # Compile OS classes first to populate symbol table
    compile_os_classes(symbol_table)

    # Process command line argument
    input_path = sys.argv[1]
    real_path = str(Path(input_path).resolve())

    if input_path.endswith(".jack"):
        # Single file
        real_path = str(Path(input_path).resolve().parent)
        os.chdir(real_path)
    else:
        # Directory
        os.chdir(os.path.realpath(input_path))

    # First pass: build symbol table for all classes
    compile_directory(os.getcwd(), symbol_table)

    # Second pass: compile using complete symbol table
    for folder_name, _, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            if filename.endswith('.xml') and 'Token' in filename:
                base_name = filename[:filename.index('Token')]
                output_string = os.path.join(folder_name, base_name)
                token_xml_path = os.path.join(folder_name, filename)
                Parser(token_xml_path, output_string, symbol_table)


if __name__ == '__main__':
    main()
