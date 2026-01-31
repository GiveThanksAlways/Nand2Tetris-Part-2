"""
VM Translator - Translates VM code to Hack assembly language.

Part of the Nand2Tetris course (Project 08).
Handles stack arithmetic, memory access, program flow, and function commands.
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
    elif 'label' in command:
        return 'C_LABEL'
    elif 'if' in command:
        return 'C_IF'
    elif 'goto' in command:
        return 'C_GOTO'
    elif 'function' in command:
        return 'C_FUNCTION'
    elif 'call' in command:
        return 'C_CALL'
    elif 'return' in command:
        return 'C_RETURN'
    elif any(op in command for op in ARITHMETIC_OPS):
        return "C_ARITHMETIC"
    return ""


def get_arg0(command: str) -> Optional[str]:
    """Get the command name (first part of VM command)."""
    parts = command.split(' ')
    if len(parts) > 0:
        return parts[0]
    return None


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


def write_init() -> None:
    """Write VM bootstrap code."""
    write_lines(['@256', 'D=A', '@SP', 'M=D'])
    write_call('Sys.init', 0, 0)


def write_label(current_function: str, label: str) -> None:
    """Write assembly code for label command."""
    write_lines([f'({current_function}${label})'])


def write_label_function(label: str) -> None:
    """Write assembly code for function label."""
    write_lines([f'({label})'])


def write_goto(current_function: str, label: str) -> None:
    """Write assembly code for goto command."""
    write_lines([f'@{current_function}${label}', '0;JMP'])


def write_goto_function(label: str) -> None:
    """Write assembly code for function goto."""
    write_lines([f'@{label}', '0;JMP'])


def write_if(current_function: str, label: str) -> None:
    """Write assembly code for if-goto command."""
    write_lines([
        '@SP', 'M=M-1', '@SP', 'A=M', 'D=M',
        f'@{current_function}${label}', 'D;JNE'
    ])


def write_if_function(label: str) -> None:
    """Write assembly code for function if-goto."""
    write_lines([
        '@SP', 'M=M-1', '@SP', 'A=M', 'D=M',
        f'@{label}', 'D;JNE'
    ])


def write_call(function_name: str, num_args: int, label_index: int) -> None:
    """Write assembly code for call command."""
    write_lines([f'@return-address{label_index}', 'D=A', "@SP", 'A=M', 'M=D', '@SP', 'M=M+1'])
    push_memory('LCL')
    push_memory('ARG')
    push_memory('THIS')
    push_memory('THAT')
    write_lines([
        '@SP', 'D=M', '@5', 'D=D-A', f'@{num_args}', 'D=D-A',
        '@ARG', 'M=D', '@SP', 'D=M', '@LCL', 'M=D'
    ])
    write_goto_function(function_name)
    write_label_function(f'return-address{label_index}')


def write_return() -> None:
    """Write assembly code for return command."""
    # R13 is FRAME, R14 is RET
    write_lines([
        '@LCL', 'D=M', '@R13', 'M=D',
        '@5', 'A=D-A', 'D=M', '@R14', 'M=D',
        "@SP", 'A=M-1', 'D=M', '@ARG', 'A=M', 'M=D',
        '@SP', 'M=M-1',
        '@ARG', 'D=M+1', '@SP', 'M=D',
        '@R13', 'A=M-1', 'D=M', '@THAT', 'M=D',
        '@R13', 'A=M-1', 'A=A-1', 'D=M', '@THIS', 'M=D',
        '@R13', 'A=M-1', 'A=A-1', 'A=A-1', 'D=M', '@ARG', 'M=D',
        '@R13', 'A=M-1', 'A=A-1', 'A=A-1', 'A=A-1', 'D=M', '@LCL', 'M=D',
        '@R14', 'A=M', '0;JMP'
    ])


def write_function(function_name: str, num_locals: int) -> None:
    """Write assembly code for function command."""
    write_label_function(function_name)
    for _ in range(num_locals):
        write_lines(['@0', 'D=A', "@SP", 'A=M', 'M=D', '@SP', 'M=M+1'])


def push_memory(item: str) -> None:
    """Push a memory segment pointer to the stack."""
    write_lines([f'@{item}', 'D=M', "@SP", 'A=M', 'M=D', '@SP', 'M=M+1'])


def main() -> None:
    """Main function to translate VM files to assembly."""
    global output

    directory_name = sys.argv[1]
    real_path = str(Path(sys.argv[1]).resolve())

    # Handle file vs directory input
    init_vm = False
    if sys.argv[1].endswith(".vm"):
        real_path = str(real_path.rpartition("/")[0])
        os.chdir(real_path)
    else:
        os.chdir(os.path.realpath(directory_name))
        init_vm = True

    asm_filename = os.getcwd().rpartition("/")[2]

    # Get all .vm files
    vm_files = [f for f in os.listdir(".") if f.endswith(".vm")]

    output = open(f"{asm_filename}.asm", 'w')

    # Write bootstrap code if processing a directory
    if init_vm:
        current_function = 'Sys.init'
        write_init()

    for vm_file in vm_files:
        content = []
        with open(vm_file) as f:
            for line in f:
                line = line.split('//', 1)[0].strip()
                if line:
                    content.append(line)

        print(content)

        base_name = vm_file[:vm_file.index('.')]
        label_counter = 2
        current_function = 'main'

        for command in content:
            arg0 = get_arg0(command)
            arg1 = get_arg1(command)
            arg2 = get_arg2(command)
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
            elif cmd_type == 'C_GOTO':
                write_goto(current_function, arg1)
            elif cmd_type == 'C_IF':
                write_if(current_function, arg1)
            elif cmd_type == 'C_RETURN':
                write_return()
            elif cmd_type == 'C_CALL':
                write_call(arg1, arg2, label_counter)
                label_counter += 1
            elif cmd_type == 'C_FUNCTION':
                current_function = arg1
                write_function(arg1, arg2)
            elif cmd_type == 'C_LABEL':
                write_label(current_function, arg1)

    output.close()


if __name__ == "__main__":
    main()
