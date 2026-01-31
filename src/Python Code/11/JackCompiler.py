"""
Jack Compiler - Compiles Jack source code to VM code.

Main entry point for the Jack compiler.
Part of the Nand2Tetris course (Project 11).
"""

import os
import sys
from pathlib import Path
from typing import List

from Tokenizer import token_type, token_wrap, inside_a_string
from Parser import Parser
from SymbolTable import SymbolTable


def read_and_clean_source(filepath: str) -> List[str]:
    """Read a Jack source file and remove comments and whitespace."""
    content = []
    with open(filepath) as f:
        for line in f:
            line = line.lstrip(' ')
            if not (line.startswith("//") or line.startswith("/**") or 
                    line.startswith("*") or line.startswith("*/")):
                line = line.split('//', 1)[0].strip()
                if line:
                    content.append(line)
    return content


def tokenize_content(content: List[str]) -> List[str]:
    """Convert source content into a list of tokens."""
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

    tokens_to_print = [x.strip() for x in tokens_to_print if x.strip()]
    return tokens_to_print


def write_tokens_xml(tokens: List[str], output_path: str) -> None:
    """Write tokens as XML to output file."""
    xml_tokens_list = ['<tokens>']
    for token in tokens:
        token_wrap(xml_tokens_list, token)
    xml_tokens_list.append('</tokens>')

    with open(output_path, 'w') as output:
        for item in xml_tokens_list:
            output.write(f"{item}\n")


def process_jack_files(folder_path: str, file_list: List[str], symbol_table: SymbolTable) -> None:
    """Process a list of Jack files in a given folder."""
    for filename in file_list:
        file_in_dir = os.path.join(folder_path, filename)
        content = read_and_clean_source(file_in_dir)
        tokens = tokenize_content(content)

        base_name = filename[:filename.index('.')]
        output_string = os.path.join(folder_path, base_name)
        output_token_string = os.path.join(folder_path, f"{base_name}Token.xml")

        write_tokens_xml(tokens, output_token_string)
        Parser(output_token_string, output_string, symbol_table)


def main() -> None:
    """Main function to compile Jack source files."""
    # Create global symbol table
    parser_symbol_table = SymbolTable()

    # First pass: Parse OS directory to get OS class definitions
    os_directory = "OS"
    if os.path.exists(os_directory):
        os_folder_path = str(Path(os_directory).resolve())
        original_dir = os.getcwd()
        os.chdir(os.path.realpath(os_directory))
        
        os_files = [f for f in os.listdir(".") if f.endswith(".jack")]
        for filename in os_files:
            content = read_and_clean_source(filename)
            tokens = tokenize_content(content)
            
            output_string = os.path.join(os_folder_path, filename[:filename.index('.')])
            output_token_string = f"{filename[:filename.index('.')]}Token.xml"
            
            write_tokens_xml(tokens, os.path.join(os_folder_path, output_token_string))
            Parser(os.path.join(os_folder_path, output_token_string), output_string, parser_symbol_table)
        
        os.chdir(original_dir)

    # Second pass: Process user input files
    directory_name = sys.argv[1]
    real_path = str(Path(sys.argv[1]).resolve())

    if sys.argv[1].endswith(".jack"):
        real_path = str(real_path.rpartition("/")[0])
        os.chdir(real_path)
    else:
        os.chdir(os.path.realpath(directory_name))

    # First loop: Build symbol table for all classes
    for folder_name, subfolders, filenames in os.walk(os.getcwd()):
        jack_files = [f for f in filenames if f.endswith('.jack')]
        if jack_files:
            for filename in jack_files:
                file_in_dir = os.path.join(folder_name, filename)
                content = read_and_clean_source(file_in_dir)
                tokens = tokenize_content(content)
                
                base_name = filename[:filename.index('.')]
                output_string = os.path.join(folder_name, base_name)
                output_token_string = os.path.join(folder_name, f"{base_name}Token.xml")
                
                write_tokens_xml(tokens, output_token_string)
                Parser(output_token_string, output_string, parser_symbol_table)

    # Second loop: Parse with complete symbol table
    for folder_name, subfolders, filenames in os.walk(os.getcwd()):
        token_files = [f for f in filenames if f.endswith('.xml') and 'Token' in f]
        for filename in token_files:
            base_name = filename[:filename.index('Token')]
            output_string = os.path.join(folder_name, base_name)
            Parser(os.path.join(folder_name, filename), output_string, parser_symbol_table)


if __name__ == "__main__":
    main()
