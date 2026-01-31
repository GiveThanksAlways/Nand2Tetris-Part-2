"""
Tokenizer module for the Jack compiler.

This module provides functions to tokenize Jack source code into XML-wrapped
tokens for subsequent parsing.
"""

from typing import List, Optional

# Jack language keywords
KEYWORDS: List[str] = [
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
    'let', 'do', 'if', 'else', 'while', 'return'
]

# Jack language symbols
SYMBOLS: List[str] = [
    '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
    '&', '|', '<', '>', '=', '~', '^'
]

# Non-terminal elements for parsing
NON_TERMINALS: List[str] = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList', 'subroutineBody',
    'varDec', 'statements', 'whileStatement', 'ifStatement', 'returnStatement',
    'letStatement', 'doStatement', 'expression', 'term', 'expressionList'
]


def print_xml_tag(token_list: List[str], content: str, tag: str) -> None:
    """Append an XML-wrapped token to the token list."""
    token_list.append(f'<{tag}> {content} </{tag}>')


def token_type(token: str) -> Optional[str]:
    """
    Determine the type of a Jack token.

    Args:
        token: The token string to classify.

    Returns:
        The token type: 'keyword', 'symbol', 'stringConstant',
        'integerConstant', 'identifier', or None.
    """
    if token in KEYWORDS:
        return 'keyword'

    if '"' in token or "'" in token:
        return 'stringConstant'

    if token in SYMBOLS:
        return 'symbol'

    if token.isdigit():
        return 'integerConstant'

    if isinstance(token, str):
        return 'identifier'

    return None


def inside_a_string(quote_counter: int) -> bool:
    """Check if currently inside a string literal based on quote count."""
    return quote_counter % 2 == 1


def token_wrap(token_list: List[str], token: str) -> None:
    """
    Wrap a token in appropriate XML tags and append to the token list.

    Args:
        token_list: The list to append the wrapped token to.
        token: The token to wrap.
    """
    ttype = token_type(token)

    if ttype == 'symbol':
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


# Backwards compatibility aliases
tokenType = token_type
insideAstring = inside_a_string
tokenWrap = token_wrap
