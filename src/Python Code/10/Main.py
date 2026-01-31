"""
Jack Analyzer Main - Entry point for Jack syntax analyzer.

Alternative entry point for the Jack Analyzer.
Part of the Nand2Tetris course (Project 10).
"""

import os
import sys
from pathlib import Path
from typing import List

from Tokenizer import token_type, token_wrap, inside_a_string
from Parser import Parser


def read_and_clean_source(filepath: str) -> List[str]:
    """Read a Jack source file and remove comments and whitespace."""
    content = []
    with open(filepath) as f:
        for line in f:
            line = line.lstrip(' ')
            # Skip comment lines
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

    # Clean up tokens
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


def main() -> None:
    """Main function to analyze Jack source files."""
    directory_name = sys.argv[1]
    real_path = str(Path(sys.argv[1]).resolve())

    # Handle file vs directory input
    if sys.argv[1].endswith(".jack"):
        real_path = str(real_path.rpartition("/")[0])
        os.chdir(real_path)
    else:
        os.chdir(os.path.realpath(directory_name))

    # Get all .jack files
    jack_files = [f for f in os.listdir(".") if f.endswith(".jack")]

    for filename in jack_files:
        content = read_and_clean_source(filename)
        tokens = tokenize_content(content)

        # Generate output filenames
        base_name = filename[:filename.index('.')]
        output_xml = f"{base_name}.xml"
        output_token_xml = f"{base_name}Token.xml"

        # Write token XML
        write_tokens_xml(tokens, output_token_xml)

        # Parse tokens
        Parser(output_token_xml, output_xml)


if __name__ == "__main__":
    main()
