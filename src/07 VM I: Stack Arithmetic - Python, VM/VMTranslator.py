"""
VM Translator for the Hack computer.

This module translates VM (Virtual Machine) code to Hack assembly language.
It handles stack arithmetic operations and memory access commands as part
of the Nand2Tetris course (Project 7).
"""

import os
import sys
from pathlib import Path
from typing import IO, List, Optional

# Assembly instruction constants
PUSH_ASM = ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
ADD_ASM = ["@SP", "M=M-1", "A=M-1", "D=M", "@SP", "A=M", "D=D+M", "@SP", "A=M-1", "M=D"]
SUB_ASM = ["@SP", "M=M-1", "A=M-1", "D=M", "@SP", "A=M", "D=D-M", "@SP", "A=M-1", "M=D"]
NEG_ASM = ["@SP", "A=M-1", "D=-M", "@SP", "A=M-1", "M=D"]
AND_ASM = ["@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D&M", "@SP", "A=M-1", "M=D"]
OR_ASM = ["@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D|M", "@SP", "A=M-1", "M=D"]
NOT_ASM = ["@SP", "A=M-1", "D=M", "D=!D", "@SP", "A=M-1", "M=D"]

# Arithmetic operations for command type detection
ARITHMETIC_OPS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}


def get_command_type(command: str) -> Optional[str]:
    """
    Determine the type of VM command.

    Args:
        command: The VM command string to analyze.

    Returns:
        A string indicating the command type (e.g., 'C_PUSH', 'C_ARITHMETIC').
    """
    if "push" in command:
        return "C_PUSH"
    elif "pop" in command:
        return "C_POP"
    elif any(op in command for op in ARITHMETIC_OPS):
        return "C_ARITHMETIC"
    elif "label" in command:
        return "C_LABEL"
    elif "goto" in command:
        return "C_GOTO"
    elif "if" in command:
        return "C_IF"
    elif "function" in command:
        return "C_FUNCTION"
    elif "call" in command:
        return "C_CALL"
    elif "return" in command:
        return "C_RETURN"
    return None


def get_arg1(command: str) -> Optional[str]:
    """
    Extract the first argument from a VM command.

    Args:
        command: The VM command string.

    Returns:
        The first argument of the command, or None if not present.
    """
    parts = command.split(" ")
    if len(parts) > 1:
        return parts[1]
    return None


def get_arg2(command: str) -> Optional[int]:
    """
    Extract the second argument from a VM command.

    Args:
        command: The VM command string.

    Returns:
        The second argument as an integer, or None if not present.
    """
    parts = command.split(" ")
    if len(parts) > 2:
        return int(parts[2])
    return None


def write_instructions(output_file: IO[str], instructions: List[str]) -> None:
    """
    Write assembly instructions to the output file.

    Args:
        output_file: The file object to write to.
        instructions: List of assembly instruction strings.
    """
    for instruction in instructions:
        output_file.write(instruction)
        output_file.write("\n")


def write_push_asm(output_file: IO[str]) -> None:
    """Write the standard push-to-stack assembly code."""
    write_instructions(output_file, PUSH_ASM)


def write_add_asm(output_file: IO[str]) -> None:
    """Write assembly code for the add operation."""
    write_instructions(output_file, ADD_ASM)


def write_sub_asm(output_file: IO[str]) -> None:
    """Write assembly code for the subtract operation."""
    write_instructions(output_file, SUB_ASM)


def write_neg_asm(output_file: IO[str]) -> None:
    """Write assembly code for the negate operation."""
    write_instructions(output_file, NEG_ASM)


def write_eq_asm(output_file: IO[str], label_index: int) -> None:
    """Write assembly code for the equality comparison."""
    eq_asm = [
        "@SP",
        "M=M-1",
        "@SP",
        "A=M-1",
        "D=M",
        "@SP",
        "A=M",
        "D=D-M",
        f"@TRUE{label_index}",
        "D;JEQ",
        "@SP",
        "A=M-1",
        "M=0",
        f"@END{label_index}",
        "0;JMP",
        f"(TRUE{label_index})",
        "@SP",
        "A=M-1",
        "M=-1",
        f"(END{label_index})",
    ]
    write_instructions(output_file, eq_asm)


def write_gt_asm(output_file: IO[str], label_index: int) -> None:
    """Write assembly code for the greater-than comparison."""
    gt_asm = [
        "@SP",
        "M=M-1",
        "@SP",
        "A=M-1",
        "D=M",
        "@SP",
        "A=M",
        "D=D-M",
        f"@TRUE{label_index}",
        "D;JGT",
        "@SP",
        "A=M-1",
        "M=0",
        f"@END{label_index}",
        "0;JMP",
        f"(TRUE{label_index})",
        "@SP",
        "A=M-1",
        "M=-1",
        f"(END{label_index})",
    ]
    write_instructions(output_file, gt_asm)


def write_lt_asm(output_file: IO[str], label_index: int) -> None:
    """Write assembly code for the less-than comparison."""
    lt_asm = [
        "@SP",
        "M=M-1",
        "@SP",
        "A=M-1",
        "D=M",
        "@SP",
        "A=M",
        "D=D-M",
        f"@TRUE{label_index}",
        "D;JLT",
        "@SP",
        "A=M-1",
        "M=0",
        f"@END{label_index}",
        "0;JMP",
        f"(TRUE{label_index})",
        "@SP",
        "A=M-1",
        "M=-1",
        f"(END{label_index})",
    ]
    write_instructions(output_file, lt_asm)


def write_and_asm(output_file: IO[str]) -> None:
    """Write assembly code for the bitwise AND operation."""
    write_instructions(output_file, AND_ASM)


def write_or_asm(output_file: IO[str]) -> None:
    """Write assembly code for the bitwise OR operation."""
    write_instructions(output_file, OR_ASM)


def write_not_asm(output_file: IO[str]) -> None:
    """Write assembly code for the bitwise NOT operation."""
    write_instructions(output_file, NOT_ASM)


def write_push_item(
    output_file: IO[str], command: str, base_filename: str
) -> None:
    """
    Write assembly code to load a value for pushing onto the stack.

    Args:
        output_file: The file object to write to.
        command: The push command string.
        base_filename: The base name of the VM file (for static variables).
    """
    segment = get_arg1(command)
    index = get_arg2(command)

    if segment == "constant":
        output_file.write(f"@{index}\n")
        output_file.write("D=A\n")
    elif segment == "argument":
        write_instructions(
            output_file, [f"@{index}", "D=A", "@ARG", "A=M+D", "D=M"]
        )
    elif segment == "local":
        write_instructions(
            output_file, [f"@{index}", "D=A", "@LCL", "A=M+D", "D=M"]
        )
    elif segment == "this":
        write_instructions(
            output_file, [f"@{index}", "D=A", "@THIS", "A=M+D", "D=M"]
        )
    elif segment == "that":
        write_instructions(
            output_file, [f"@{index}", "D=A", "@THAT", "A=M+D", "D=M"]
        )
    elif segment == "static":
        write_instructions(output_file, [f"@{base_filename}.{index}", "D=M"])
    elif segment == "pointer":
        write_instructions(
            output_file, [f"@{index}", "D=A", "@THIS", "A=A+D", "D=M"]
        )
    elif segment == "temp":
        write_instructions(
            output_file, [f"@{index}", "D=A", "@5", "A=A+D", "D=M"]
        )


def write_pop_asm(
    output_file: IO[str], command: str, base_filename: str
) -> None:
    """
    Write assembly code for the pop command.

    Args:
        output_file: The file object to write to.
        command: The pop command string.
        base_filename: The base name of the VM file (for static variables).
    """
    segment = get_arg1(command)
    index = get_arg2(command)

    if segment != "static":
        write_instructions(
            output_file,
            ["@SP", "A=M-1", "D=M", "@R15", "M=D", f"@{index}", "D=A"],
        )

    if segment == "constant":
        output_file.write(f"@{index}\n")
        output_file.write("M=D\n")
    elif segment == "argument":
        write_instructions(output_file, ["@ARG"])
    elif segment == "local":
        write_instructions(output_file, ["@LCL"])
    elif segment == "this":
        write_instructions(output_file, ["@THIS"])
    elif segment == "that":
        write_instructions(output_file, ["@THAT"])
    elif segment == "static":
        write_instructions(
            output_file,
            ["@SP", "A=M-1", "D=M", f"@{base_filename}.{index}", "M=D"],
        )
    elif segment == "pointer":
        write_instructions(output_file, ["@THIS", "D=A+D"])
    elif segment == "temp":
        write_instructions(output_file, ["@5", "D=A+D"])

    pop_end_asm = [
        "D=M+D",
        "@R14",
        "M=D",
        "@R15",
        "D=M",
        "@R14",
        "A=M",
        "M=D",
        "@SP",
        "M=M-1",
    ]

    if segment in ("pointer", "temp"):
        write_instructions(
            output_file,
            ["@R14", "M=D", "@R15", "D=M", "@R14", "A=M", "M=D", "@SP", "M=M-1"],
        )
    elif segment == "static":
        write_instructions(output_file, ["@SP", "M=M-1"])
    else:
        write_instructions(output_file, pop_end_asm)


def process_command(
    output_file: IO[str],
    command: str,
    base_filename: str,
    label_counter: int,
) -> int:
    """
    Process a single VM command and write corresponding assembly.

    Args:
        output_file: The file object to write to.
        command: The VM command to process.
        base_filename: The base name of the VM file.
        label_counter: Current counter for unique labels.

    Returns:
        Updated label counter.
    """
    command_type = get_command_type(command)

    if command_type == "C_PUSH":
        write_push_item(output_file, command, base_filename)
        write_push_asm(output_file)
    elif command_type == "C_ARITHMETIC":
        if "add" in command:
            write_add_asm(output_file)
        elif "sub" in command:
            write_sub_asm(output_file)
        elif "neg" in command:
            write_neg_asm(output_file)
        elif "eq" in command:
            write_eq_asm(output_file, label_counter)
            label_counter += 1
        elif "gt" in command:
            write_gt_asm(output_file, label_counter)
            label_counter += 1
        elif "lt" in command:
            write_lt_asm(output_file, label_counter)
            label_counter += 1
        elif "and" in command:
            write_and_asm(output_file)
        elif "or" in command:
            write_or_asm(output_file)
        elif "not" in command:
            write_not_asm(output_file)
    elif command_type == "C_POP":
        write_pop_asm(output_file, command, base_filename)

    return label_counter


def parse_vm_file(filepath: str) -> List[str]:
    """
    Parse a VM file and return cleaned commands.

    Args:
        filepath: Path to the VM file.

    Returns:
        List of cleaned VM commands.
    """
    commands = []
    with open(filepath) as vm_file:
        for line in vm_file:
            line = line.split("//", 1)[0]
            line = line.strip()
            if line:
                commands.append(line)
    return commands


def translate_vm_files(input_path: str) -> None:
    """
    Translate VM files to Hack assembly.

    Args:
        input_path: Path to a VM file or directory containing VM files.
    """
    real_path = str(Path(input_path).resolve())

    if input_path.endswith(".vm"):
        directory_path = str(Path(real_path).parent)
        os.chdir(directory_path)
        asm_filename = input_path.split("/")[-1].replace(".vm", "")
    else:
        os.chdir(os.path.realpath(input_path))
        asm_filename = os.path.basename(os.getcwd())

    vm_files = [f for f in os.listdir(".") if f.endswith(".vm")]

    with open(f"{asm_filename}.asm", "w") as output_file:
        for vm_filename in vm_files:
            commands = parse_vm_file(vm_filename)
            base_filename = vm_filename[: vm_filename.index(".")]
            label_counter = 0

            for command in commands:
                label_counter = process_command(
                    output_file, command, base_filename, label_counter
                )


def main() -> None:
    """Main entry point for the VM translator."""
    if len(sys.argv) < 2:
        print("Usage: python VMTranslator.py <file.vm | directory>")
        sys.exit(1)

    translate_vm_files(sys.argv[1])


if __name__ == "__main__":
    main()
