"""
VM Translator - Translates VM code to Hack assembly language.

Part of the Nand2Tetris course (Project 07).
Handles stack arithmetic and memory access commands.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Global output file handle
output = None

# Arithmetic operations
ARITHMETIC_OPS = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']


def command_type(command: str) -> str:
    """Determine the type of VM command."""
    if "push" in command:
        return "C_PUSH"
    elif "pop" in command:
        return "C_POP"
    elif any(op in command for op in ARITHMETIC_OPS):
        return "C_ARITHMETIC"
    elif 'label' in command:
        return 'C_LABEL'
    elif 'goto' in command:
        return 'C_GOTO'
    elif 'if' in command:
        return 'C_IF'
    elif 'function' in command:
        return 'C_FUNCTION'
    elif 'call' in command:
        return 'C_CALL'
    elif 'return' in command:
        return 'C_RETURN'
    return ""


def get_arg1(command: str) -> Optional[str]:
    """Get the first argument of a VM command."""
    parts = command.split(' ')
    if len(parts) > 1:
        return parts[1]
    return None


def get_arg2(command: str) -> Optional[int]:
    """Get the second argument of a VM command."""
    parts = command.split(' ')
    if len(parts) > 2:
        return int(parts[2])
    return None


def write_lines(lines: list) -> None:
    """Write multiple lines of assembly code to output."""
    for line in lines:
        output.write(f"{line}\n")


def write_push_asm() -> None:
    """Write assembly code for pushing D register to stack."""
    write_lines(["@SP", 'A=M', 'M=D', '@SP', 'M=M+1'])


def write_add_asm() -> None:
    """Write assembly code for add operation."""
    write_lines(["@SP", 'M=M-1', 'A=M-1', 'D=M', '@SP', 'A=M', 'D=D+M', '@SP', 'A=M-1', 'M=D'])


def write_sub_asm() -> None:
    """Write assembly code for subtract operation."""
    write_lines(["@SP", 'M=M-1', 'A=M-1', 'D=M', '@SP', 'A=M', 'D=D-M', '@SP', 'A=M-1', 'M=D'])


def write_neg_asm() -> None:
    """Write assembly code for negate operation."""
    write_lines(["@SP", 'A=M-1', 'D=-M', '@SP', 'A=M-1', 'M=D'])


def write_eq_asm(label_index: int) -> None:
    """Write assembly code for equality comparison."""
    write_lines([
        "@SP", 'M=M-1', "@SP", 'A=M-1', 'D=M', '@SP', 'A=M', 'D=D-M',
        f'@TRUE{label_index}', 'D;JEQ', '@SP', 'A=M-1', 'M=0',
        f'@END{label_index}', '0;JMP', f'(TRUE{label_index})',
        '@SP', 'A=M-1', 'M=-1', f'(END{label_index})'
    ])


def write_gt_asm(label_index: int) -> None:
    """Write assembly code for greater-than comparison."""
    write_lines([
        "@SP", 'M=M-1', "@SP", 'A=M-1', 'D=M', '@SP', 'A=M', 'D=D-M',
        f'@TRUE{label_index}', 'D;JGT', '@SP', 'A=M-1', 'M=0',
        f'@END{label_index}', '0;JMP', f'(TRUE{label_index})',
        '@SP', 'A=M-1', 'M=-1', f'(END{label_index})'
    ])


def write_lt_asm(label_index: int) -> None:
    """Write assembly code for less-than comparison."""
    write_lines([
        "@SP", 'M=M-1', "@SP", 'A=M-1', 'D=M', '@SP', 'A=M', 'D=D-M',
        f'@TRUE{label_index}', 'D;JLT', '@SP', 'A=M-1', 'M=0',
        f'@END{label_index}', '0;JMP', f'(TRUE{label_index})',
        '@SP', 'A=M-1', 'M=-1', f'(END{label_index})'
    ])


def write_and_asm() -> None:
    """Write assembly code for bitwise AND operation."""
    write_lines([
        "@SP", 'M=M-1', "@SP", 'A=M-1', 'D=M', '@SP', 'A=M',
        'D=D&M', '@SP', 'A=M-1', 'M=D'
    ])


def write_or_asm() -> None:
    """Write assembly code for bitwise OR operation."""
    write_lines([
        "@SP", 'M=M-1', "@SP", 'A=M-1', 'D=M', '@SP', 'A=M',
        'D=D|M', '@SP', 'A=M-1', 'M=D'
    ])


def write_not_asm() -> None:
    """Write assembly code for bitwise NOT operation."""
    write_lines(["@SP", 'A=M-1', 'D=M', 'D=!D', '@SP', 'A=M-1', 'M=D'])


def write_push_item(command: str, filename: str) -> None:
    """Write assembly code for push command based on segment."""
    segment = get_arg1(command)
    index = get_arg2(command)

    segment_map = {
        'argument': 'ARG',
        'local': 'LCL',
        'this': 'THIS',
        'that': 'THAT'
    }

    if segment == 'constant':
        output.write(f'@{index}\nD=A\n')
    elif segment in segment_map:
        write_lines([f'@{index}', 'D=A', f'@{segment_map[segment]}', 'A=M+D', 'D=M'])
    elif segment == 'static':
        write_lines([f'@{filename}.{index}', 'D=M'])
    elif segment == 'pointer':
        write_lines([f'@{index}', 'D=A', '@THIS', 'A=A+D', 'D=M'])
    elif segment == 'temp':
        write_lines([f'@{index}', 'D=A', '@5', 'A=A+D', 'D=M'])


def write_pop_asm(command: str, filename: str) -> None:
    """Write assembly code for pop command based on segment."""
    segment = get_arg1(command)
    index = get_arg2(command)

    segment_map = {
        'argument': '@ARG',
        'local': '@LCL',
        'this': '@THIS',
        'that': '@THAT'
    }

    if segment != 'static':
        write_lines(["@SP", 'A=M-1', 'D=M', '@R15', 'M=D', f'@{index}', 'D=A'])

    if segment == 'constant':
        output.write(f'@{index}\nM=D\n')
    elif segment in segment_map:
        write_lines([segment_map[segment]])
    elif segment == 'static':
        write_lines(["@SP", 'A=M-1', 'D=M', f'@{filename}.{index}', 'M=D'])
    elif segment == 'pointer':
        write_lines(['@THIS', 'D=A+D'])
    elif segment == 'temp':
        write_lines(['@5', 'D=A+D'])

    # Write ending code based on segment type
    if segment in ['pointer', 'temp']:
        write_lines(['@R14', 'M=D', '@R15', 'D=M', '@R14', 'A=M', 'M=D', '@SP', 'M=M-1'])
    elif segment == 'static':
        write_lines(['@SP', 'M=M-1'])
    elif segment != 'constant':
        write_lines(['D=M+D', '@R14', 'M=D', '@R15', 'D=M', '@R14', 'A=M', 'M=D', '@SP', 'M=M-1'])


def main() -> None:
    """Main function to translate VM files to assembly."""
    global output

    directory_name = sys.argv[1]
    real_path = str(Path(sys.argv[1]).resolve())

    # Handle file vs directory input
    if sys.argv[1].endswith(".vm"):
        real_path = str(real_path.rpartition("/")[0])
        os.chdir(real_path)
        asm_filename = sys.argv[1].split("/")[-1].split(".vm")[0]
    else:
        os.chdir(os.path.realpath(directory_name))
        asm_filename = os.getcwd().rpartition("/")[2]

    # Get all .vm files
    vm_files = [f for f in os.listdir(".") if f.endswith(".vm")]

    output = open(f"{asm_filename}.asm", 'w')

    for vm_file in vm_files:
        with open(vm_file) as file:
            content = []
            for line in file:
                line = line.split('//', 1)[0].strip()
                if line:
                    content.append(line)

            base_name = vm_file[:vm_file.index('.')]
            label_counter = 0

            for command in content:
                cmd_type = command_type(command)

                if cmd_type == 'C_PUSH':
                    write_push_item(command, base_name)
                    write_push_asm()
                elif cmd_type == 'C_ARITHMETIC':
                    if 'add' in command:
                        write_add_asm()
                    elif 'sub' in command:
                        write_sub_asm()
                    elif 'neg' in command:
                        write_neg_asm()
                    elif 'eq' in command:
                        write_eq_asm(label_counter)
                        label_counter += 1
                    elif 'gt' in command:
                        write_gt_asm(label_counter)
                        label_counter += 1
                    elif 'lt' in command:
                        write_lt_asm(label_counter)
                        label_counter += 1
                    elif 'and' in command:
                        write_and_asm()
                    elif 'or' in command:
                        write_or_asm()
                    elif 'not' in command:
                        write_not_asm()
                elif cmd_type == 'C_POP':
                    write_pop_asm(command, base_name)

    output.close()


if __name__ == "__main__":
    main()
