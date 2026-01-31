"""
Hack Assembler - Main Module.

Translates Hack assembly language (.asm) files into Hack machine code (.hack).
This is a two-pass assembler for the Hack computer architecture from Nand2Tetris.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import code as instruction_module

# Predefined symbols for the Hack assembly language
PREDEFINED_SYMBOLS: Dict[str, int] = {
    # Virtual registers R0-R15
    'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3,
    'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
    'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
    'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
    # I/O pointers
    'SCREEN': 16384,
    'KBD': 24576,
    # VM pointers
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4
}

# Constants
A_INSTRUCTION_BITS = 15
VARIABLE_BASE_ADDRESS = 16
C_INSTRUCTION_PREFIX = '111'
NULL_BITS = '000'

INPUT_FILE = 'input.txt'
OUTPUT_FILE = 'output.txt'


def represents_int(value: str) -> bool:
    """
    Determine if a string represents an integer.

    Args:
        value: The string to check.

    Returns:
        True if the string can be converted to an integer, False otherwise.
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def read_and_clean_source(filepath: Path) -> List[str]:
    """
    Read assembly source file and remove comments and whitespace.

    Args:
        filepath: Path to the assembly source file.

    Returns:
        List of cleaned assembly instructions.
    """
    content: List[str] = []
    with open(filepath) as source_file:
        for line in source_file:
            line = line.split('//', 1)[0]
            line = line.strip()
            content.append(line)

    return [item for item in content if item != '']


def first_pass(content: List[str], symbol_table: Dict[str, int]) -> None:
    """
    First pass: Build symbol table with label addresses.

    Args:
        content: List of assembly instructions.
        symbol_table: Symbol table to populate with labels.
    """
    rom_address = 0
    for command in content:
        if "(" in command:
            label = command[1:len(command) - 1]
            symbol_table[label] = rom_address
            rom_address -= 1
        rom_address += 1


def to_binary(value: int, num_bits: int) -> str:
    """
    Convert an integer to a binary string with specified width.

    Args:
        value: The integer to convert.
        num_bits: The number of bits in the result.

    Returns:
        Binary string representation with leading zeros.
    """
    return format(value, 'b').zfill(num_bits)


def translate_a_instruction(command: str, symbol_table: Dict[str, int],
                            next_variable_address: int) -> Tuple[str, int]:
    """
    Translate an A-instruction to binary.

    Args:
        command: The A-instruction (e.g., '@100' or '@symbol').
        symbol_table: Symbol table for resolving symbols.
        next_variable_address: Next available address for new variables.

    Returns:
        Tuple of (binary instruction, updated next variable address).
    """
    symbol = command[1:]

    if not represents_int(symbol):
        if symbol not in symbol_table:
            symbol_table[symbol] = next_variable_address
            next_variable_address += 1
        address = symbol_table[symbol]
    else:
        address = int(symbol)

    binary_instruction = f"0{to_binary(address, A_INSTRUCTION_BITS)}"
    return binary_instruction, next_variable_address


def translate_c_instruction(command: str) -> str:
    """
    Translate a C-instruction to binary.

    Args:
        command: The C-instruction (e.g., 'D=A+1' or 'D;JGT').

    Returns:
        Binary representation of the C-instruction.
    """
    instruction_codes = instruction_module.INSTRUCTION_CODES
    c_command = str(command)
    comp = ''
    jump = ''
    dest = ''

    if c_command.find('=') != -1:
        dest = c_command[0:c_command.find('=')]
        comp = c_command[c_command.find('=') + 1:len(c_command)]

    if c_command.find(';') != -1:
        jump = c_command[c_command.find(';') + 1:len(c_command)]
        comp = c_command[0:c_command.find(';')]

    if jump == '':
        jump_bits = NULL_BITS
    else:
        spot = instruction_codes.index(jump) - 1
        jump_bits = instruction_codes[spot]

    if dest == '':
        dest_bits = NULL_BITS
    else:
        spot = max(loc for loc, val in enumerate(instruction_codes) if val == dest) - 1
        dest_bits = instruction_codes[spot]

    spot = instruction_codes.index(comp) - 1
    comp_bits = instruction_codes[spot]

    return f"{C_INSTRUCTION_PREFIX}{comp_bits}{dest_bits}{jump_bits}"


def second_pass(content: List[str], symbol_table: Dict[str, int],
                output_path: Path) -> None:
    """
    Second pass: Translate instructions and write binary output.

    Args:
        content: List of assembly instructions.
        symbol_table: Symbol table with all symbols resolved.
        output_path: Path to the output file.
    """
    next_variable_address = VARIABLE_BASE_ADDRESS

    with open(output_path, 'w') as output_file:
        for command in content:
            if "@" in command:
                binary, next_variable_address = translate_a_instruction(
                    command, symbol_table, next_variable_address
                )
                output_file.write(f"{binary}\n")
            elif "=" in command or ";" in command:
                binary = translate_c_instruction(command)
                output_file.write(f"{binary}\n")


def main() -> None:
    """Main entry point for the Hack assembler."""
    symbol_table = PREDEFINED_SYMBOLS.copy()
    content = read_and_clean_source(Path(INPUT_FILE))

    first_pass(content, symbol_table)
    second_pass(content, symbol_table, Path(OUTPUT_FILE))


if __name__ == '__main__':
    main()

