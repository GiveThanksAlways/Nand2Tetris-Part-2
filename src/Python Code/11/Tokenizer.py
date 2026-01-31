"""
Jack Tokenizer - Lexical analyzer for Jack programming language.

Breaks Jack source code into tokens for parsing and compilation.
Part of the Nand2Tetris course (Project 11).
"""

from typing import List

# Jack language keywords
KEYWORDS = [
    'class', 'constructor', 'function', 'method', 'field', 'static',
    'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
    'this', 'let', 'do', 'if', 'else', 'while', 'return'
]

# Jack language symbols (includes ^ for power operation)
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^']

# Non-terminal grammar elements
NON_TERMINALS = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList', 'subroutineBody',
    'varDec', 'statements', 'whileStatement', 'ifStatement', 'returnStatement',
    'letStatement', 'doStatement', 'expression', 'term', 'expressionList'
]


def print_xml_tag(token_list: List[str], content: str, tag: str) -> None:
    """Append an XML-wrapped token to the token list."""
    token_list.append(f'<{tag}> {content} </{tag}>')


def token_type(token: str) -> str:
    """Determine the type of a token."""
    if token in KEYWORDS:
        return 'keyword'

    if any(char in ['"', "'"] for char in token):
        return 'stringConstant'

    if token in SYMBOLS:
        return 'symbol'

    if token.isdigit():
        return 'integerConstant'

    if isinstance(token, str):
        return 'identifier'

    return ''


def inside_a_string(counter: int) -> bool:
    """Check if currently inside a string literal (odd quote count)."""
    return counter % 2 == 1


def token_wrap(token_list: List[str], token: str) -> None:
    """Wrap a token in appropriate XML tags and add to list."""
    ttype = token_type(token)

    if ttype == 'symbol':
        # Escape special XML characters
        if token == '>':
            print_xml_tag(token_list, '&gt;', 'symbol')
        elif token == '<':
            print_xml_tag(token_list, '&lt;', 'symbol')
        elif token == '&':
            print_xml_tag(token_list, '&amp;', 'symbol')
        else:
            print_xml_tag(token_list, token, 'symbol')
    elif ttype == 'keyword':
        print_xml_tag(token_list, token, 'keyword')
    elif ttype == 'stringConstant':
        print_xml_tag(token_list, token.strip('"'), 'stringConstant')
    elif ttype == 'integerConstant':
        print_xml_tag(token_list, token, 'integerConstant')
    elif ttype == 'identifier':
        print_xml_tag(token_list, token, 'identifier')


# Backward compatibility aliases
tokenType = token_type
insideAstring = inside_a_string
tokenWrap = token_wrap

