"""
Tokenizer module for Jack language syntax analysis.

This module provides functions for tokenizing Jack source code into XML-formatted
tokens, identifying token types (keywords, symbols, identifiers, constants).
"""

from typing import List

# Jack language keywords
KEYWORDS: List[str] = [
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
    'let', 'do', 'if', 'else', 'while', 'return'
]

# Jack language symbols
SYMBOLS: List[str] = [
    '{', '}', '(', ')', '[', ']', '.', ',', ';',
    '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
]

# Non-terminal elements in Jack grammar
NON_TERMINALS: List[str] = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList', 'subroutineBody',
    'varDec', 'statements', 'whileStatement', 'ifStatement', 'returnStatement',
    'letStatement', 'doStatement', 'expression', 'term', 'expressionList'
]


def print_xml_tag(token_list: List[str], content: str, tag: str) -> None:
    """
    Append an XML-formatted tag with content to the token list.

    Args:
        token_list: List to append the XML tag to.
        content: The content to wrap in XML tags.
        tag: The XML tag name.
    """
    token_list.append(f'<{tag}> {content} </{tag}>')


def get_token_type(token: str) -> str:
    """
    Determine the type of a Jack token.

    Args:
        token: The token string to classify.

    Returns:
        One of: 'keyword', 'symbol', 'stringConstant', 'integerConstant', 'identifier'
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

    return ''


def is_inside_string(quote_counter: int) -> bool:
    """
    Check if currently inside a string literal based on quote count.

    Args:
        quote_counter: Count of quote characters encountered.

    Returns:
        True if inside a string (odd count), False otherwise.
    """
    return quote_counter % 2 == 1


def token_wrap(token_list: List[str], token: str) -> None:
    """
    Wrap a token in appropriate XML tags and append to list.

    Handles special XML escaping for symbols like <, >, and &.

    Args:
        token_list: List to append the wrapped token to.
        token: The token to wrap.
    """
    token_type = get_token_type(token)

    if token_type == 'symbol':
        if token == '>':
            print_xml_tag(token_list, '&gt;', 'symbol')
        elif token == '<':
            print_xml_tag(token_list, '&lt;', 'symbol')
        elif token == '&':
            print_xml_tag(token_list, '&amp;', 'symbol')
        else:
            print_xml_tag(token_list, token, 'symbol')
    elif token_type == 'keyword':
        print_xml_tag(token_list, token, 'keyword')
    elif token_type == 'stringConstant':
        print_xml_tag(token_list, token.strip('"'), 'stringConstant')
    elif token_type == 'integerConstant':
        print_xml_tag(token_list, token, 'integerConstant')
    elif token_type == 'identifier':
        print_xml_tag(token_list, token, 'identifier')

