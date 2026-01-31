"""
Tokenizer module for the Jack compiler.

This module provides tokenization functionality for Jack source files,
converting raw text into classified tokens (keywords, symbols, identifiers, etc.).
"""

from typing import List, Optional

# Constants for token classification
KEYWORDS: List[str] = [
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
    'let', 'do', 'if', 'else', 'while', 'return'
]

SYMBOLS: List[str] = [
    '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
    '&', '|', '<', '>', '=', '~', '^'
]

NON_TERMINALS: List[str] = [
    'class', 'classVarDec', 'subroutineDec', 'parameterList', 'subroutineBody',
    'varDec', 'statements', 'whileStatement', 'ifStatement', 'returnStatement',
    'letStatement', 'doStatement', 'expression', 'term', 'expressionList'
]


def print_xml_tag(token_list: List[str], content: str, tag: str) -> None:
    """
    Append an XML-wrapped token to the token list.

    Args:
        token_list: List to append the XML tag to.
        content: The content to wrap in XML tags.
        tag: The XML tag name.
    """
    token_list.append(f'<{tag}> {content} </{tag}>')


def token_type(token_input: str) -> Optional[str]:
    """
    Determine the type of a given token.

    Args:
        token_input: The token string to classify.

    Returns:
        The token type as a string, or None if unclassifiable.
    """
    if token_input in KEYWORDS:
        return 'keyword'

    if any(char in ('"', "'") for char in str(token_input)):
        return 'stringConstant'

    if token_input in SYMBOLS:
        return 'symbol'

    if token_input.isdigit():
        return 'integerConstant'

    if isinstance(token_input, str):
        return 'identifier'

    return None


def inside_a_string(quote_counter: int) -> bool:
    """
    Check if the current position is inside a string literal.

    Args:
        quote_counter: The count of quote characters encountered.

    Returns:
        True if inside a string (odd count), False otherwise.
    """
    return quote_counter % 2 == 1


def token_wrap(token_list: List[str], token_input: str) -> None:
    """
    Wrap a token in appropriate XML tags and add to the token list.

    Args:
        token_list: List to append the wrapped token to.
        token_input: The token to wrap.
    """
    current_type = token_type(token_input)

    if current_type == 'symbol':
        if token_input == '>':
            print_xml_tag(token_list, '&gt;', 'symbol')
        elif token_input == '<':
            print_xml_tag(token_list, '&lt;', 'symbol')
        elif token_input == '&':
            print_xml_tag(token_list, '&amp;', 'symbol')
        else:
            print_xml_tag(token_list, token_input, 'symbol')
    elif current_type == 'keyword':
        print_xml_tag(token_list, token_input, 'keyword')
    elif current_type == 'stringConstant':
        stripped_string = str(token_input).strip('"')
        print_xml_tag(token_list, stripped_string, 'stringConstant')
    elif current_type == 'integerConstant':
        print_xml_tag(token_list, token_input, 'integerConstant')
    elif current_type == 'identifier':
        print_xml_tag(token_list, token_input, 'identifier')

