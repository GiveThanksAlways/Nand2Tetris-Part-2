"""
Hack Assembler - Main Module

Translates Hack assembly language (.asm) into binary machine code.
Part of the Nand2Tetris course (Project 06).
"""

import code

# Built-in symbol table with predefined labels and pointers
PREDEFINED_SYMBOLS = {
    'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
    'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
    'SCREEN': 16384, 'KBD': 24576,
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4
}


def represents_int(value: str) -> bool:
    """Check if a string represents an integer value."""
    try:
        int(value)
        return True
    except ValueError:
        return False


def to_binary(number: int, bits: int = 15) -> str:
    """Convert a number to binary string with specified bit width."""
    return format(number, 'b').zfill(bits)


def main() -> None:
    """Main assembler function that processes input.txt and outputs binary."""
    symbol_table = PREDEFINED_SYMBOLS.copy()
    content = []

    # Read and clean input file
    with open("input.txt") as f:
        for line in f:
            line = line.split('//', 1)[0].strip()
            if line:
                content.append(line)

    # First pass: Build symbol table with labels
    rom_address = 0
    for command in content:
        if command.startswith("("):
            label = command[1:-1]
            symbol_table[label] = rom_address
        else:
            rom_address += 1

    # Second pass: Generate binary code
    ram_address = 16
    with open('output.txt', 'w') as output:
        for command in content:
            if command.startswith("("):
                continue

            if command.startswith("@"):
                # A-instruction
                symbol = command[1:]
                if not represents_int(symbol):
                    if symbol not in symbol_table:
                        symbol_table[symbol] = ram_address
                        ram_address += 1
                    value = symbol_table[symbol]
                else:
                    value = int(symbol)
                binary_value = f"0{to_binary(value)}\n"
                output.write(binary_value)

            elif "=" in command or ";" in command:
                # C-instruction
                dest = ''
                comp = ''
                jump = ''

                if '=' in command:
                    dest = command[:command.find('=')]
                    comp = command[command.find('=') + 1:]

                if ';' in command:
                    jump = command[command.find(';') + 1:]
                    comp = command[:command.find(';')] if '=' not in command else comp[:comp.find(';')]

                # Look up binary codes
                jump_code = "000" if not jump else code.INSTRUCTION_TABLE[code.INSTRUCTION_TABLE.index(jump) - 1]
                dest_code = "000" if not dest else code.INSTRUCTION_TABLE[max(i for i, v in enumerate(code.INSTRUCTION_TABLE) if v == dest) - 1]
                comp_code = code.INSTRUCTION_TABLE[code.INSTRUCTION_TABLE.index(comp) - 1]

                output.write(f"111{comp_code}{dest_code}{jump_code}\n")


if __name__ == "__main__":
    main()

