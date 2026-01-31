"""
Instruction codes module for the Hack Assembler.

Contains binary codes for computation, destination, and jump mnemonics
used to translate Hack assembly C-instructions into machine code.
"""

from typing import List

# Instruction codes list containing pairs of [binary_code, mnemonic]
# Used for lookup during C-instruction translation
# Format: comp codes (a=0), comp codes (a=1), dest codes, jump codes
INSTRUCTION_CODES: List[str] = [
    # Computation codes when a=0 (using A register)
    '0101010', '0',
    '0111111', '1',
    '0111010', '-1',
    '0001100', 'D',
    '0110000', 'A',
    '0001101', '!D',
    '0110001', '!A',
    '0001111', '-D',
    '0110011', '-A',
    '0011111', 'D+1',
    '0110111', 'A+1',
    '0001110', 'D-1',
    '0110010', 'A-1',
    '0000010', 'D+A',
    '0010011', 'D-A',
    '0000111', 'A-D',
    '0000000', 'D&A',
    '0010101', 'D|A',
    # Computation codes when a=1 (using M register)
    '1101010', '0',
    '1111111', '1',
    '1111010', '-1',
    '1001100', 'D',
    '1110000', 'M',
    '1001101', '!D',
    '1110001', '!M',
    '1001111', '-D',
    '1110011', '-M',
    '1011111', 'D+1',
    '1110111', 'M+1',
    '1001110', 'D-1',
    '1110010', 'M-1',
    '1000010', 'D+M',
    '1010011', 'D-M',
    '1000111', 'M-D',
    '1000000', 'D&M',
    '1010101', 'D|M',
    # Destination codes and Jump codes (interleaved)
    '001', 'M',   '001', 'JGT',
    '010', 'D',   '010', 'JEQ',
    '011', 'MD',  '011', 'JGE',
    '100', 'A',   '100', 'JLT',
    '101', 'AM',  '101', 'JNE',
    '110', 'AD',  '110', 'JLE',
    '111', 'AMD', '111', 'JMP'
]

