"""
Jack Analyzer - Main entry point for Jack language syntax analysis.

This module processes Jack source files, tokenizes them, and generates
XML parse trees. It can process individual .jack files or entire directories.
"""

import os
import sys
from pathlib import Path
from typing import List

from Parser import Parser
from Tokenizer import get_token_type, is_inside_string, token_wrap


def read_jack_file(filename: str) -> List[str]:
    """
    Read and preprocess a Jack source file.

    Removes comments and whitespace, returning clean source lines.

    Args:
        filename: Path to the Jack source file.

    Returns:
        List of cleaned source code lines.
    """
    content: List[str] = []
    with open(filename) as f:
        for line in f:
            line = line.lstrip(' ')
            # Skip comment lines
            if not (line.startswith("//") or line.startswith("/**") or
                    line.startswith("*") or line.startswith("*/")):
                # Remove trailing comments
                line = line.split('//', 1)[0]
                line = line.rstrip()
                content.append(line)

    # Clean and filter empty lines
    content = [x.strip() for x in content]
    return [item for item in content if item != '']


def tokenize_content(content: List[str]) -> List[str]:
    """
    Tokenize Jack source content into a list of tokens.

    Args:
        content: List of preprocessed source lines.

    Returns:
        List of token strings.
    """
    token_buffer: List[str] = []
    tokens: List[str] = []
    quote_counter: int = 0

    for line in content:
        for char in line:
            # Track string literal boundaries
            if char == '"':
                quote_counter += 1

            if is_inside_string(quote_counter):
                token_buffer.append(char)
            elif char != ' ':
                if get_token_type(char) == 'symbol':
                    tokens.append(''.join(token_buffer))
                    token_buffer = [char]
                    tokens.append(''.join(token_buffer))
                    token_buffer = []
                else:
                    token_buffer.append(char)
            else:
                tokens.append(''.join(token_buffer))
                token_buffer = []

    # Clean and filter empty tokens
    tokens = [x.strip() for x in tokens]
    return [item for item in tokens if item != '']


def write_token_xml(tokens: List[str], output_path: str) -> None:
    """
    Write tokens to an XML file.

    Args:
        tokens: List of token strings.
        output_path: Path for the output XML file.
    """
    xml_tokens: List[str] = ['<tokens>']
    for token in tokens:
        token_wrap(xml_tokens, token)
    xml_tokens.append('</tokens>')

    with open(output_path, 'w') as output:
        for item in xml_tokens:
            output.write(item)
            output.write('\n')


def process_jack_file(filename: str) -> None:
    """
    Process a single Jack file through tokenization and parsing.

    Args:
        filename: Name of the Jack source file.
    """
    base_name = filename[:filename.index('.')]
    output_xml = f'{base_name}.xml'
    token_xml = f'{base_name}Token.xml'

    content = read_jack_file(filename)
    tokens = tokenize_content(content)
    write_token_xml(tokens, token_xml)
    Parser(token_xml, output_xml)


def main() -> None:
    """Main entry point for the Jack Analyzer."""
    if len(sys.argv) < 2:
        print("Usage: python JackAnalyzer.py <file.jack | directory>")
        sys.exit(1)

    input_path = sys.argv[1]
    real_path = str(Path(input_path).resolve())

    # Determine working directory
    if input_path.endswith(".jack"):
        work_dir = str(Path(real_path).parent)
        os.chdir(work_dir)
    else:
        os.chdir(os.path.realpath(input_path))

    # Find all Jack files
    jack_files = [f for f in os.listdir(".") if f.endswith(".jack")]

    # Process each Jack file
    for filename in jack_files:
        process_jack_file(filename)


if __name__ == "__main__":
    main()
