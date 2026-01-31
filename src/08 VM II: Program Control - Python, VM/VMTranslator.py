"""
VM Translator for Hack Assembly Language.

This module translates VM (Virtual Machine) code to Hack assembly language,
supporting arithmetic operations, memory access, program flow (labels, goto, if-goto),
and function calls (call, function, return).
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, TextIO

# Assembly instruction constants
PUSH_ASM = ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
ADD_ASM = ["@SP", "M=M-1", "A=M-1", "D=M", "@SP", "A=M", "D=D+M", "@SP", "A=M-1", "M=D"]
SUB_ASM = ["@SP", "M=M-1", "A=M-1", "D=M", "@SP", "A=M", "D=D-M", "@SP", "A=M-1", "M=D"]
NEG_ASM = ["@SP", "A=M-1", "D=-M", "@SP", "A=M-1", "M=D"]
AND_ASM = ["@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D&M", "@SP", "A=M-1", "M=D"]
OR_ASM = ["@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D|M", "@SP", "A=M-1", "M=D"]
NOT_ASM = ["@SP", "A=M-1", "D=M", "D=!D", "@SP", "A=M-1", "M=D"]
ARITHMETIC_OPERATIONS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}


def get_command_type(command: str) -> Optional[str]:
    """
    Determine the type of VM command.

    Args:
        command: The VM command string to classify.

    Returns:
        A string representing the command type (e.g., 'C_PUSH', 'C_ARITHMETIC').
    """
    if "push" in command:
        return "C_PUSH"
    elif "pop" in command:
        return "C_POP"
    elif "label" in command:
        return "C_LABEL"
    elif "if" in command:
        return "C_IF"
    elif "goto" in command:
        return "C_GOTO"
    elif "function" in command:
        return "C_FUNCTION"
    elif "call" in command:
        return "C_CALL"
    elif "return" in command:
        return "C_RETURN"
    elif any(op in command for op in ARITHMETIC_OPERATIONS):
        return "C_ARITHMETIC"
    return None


def get_arg0(command: str) -> Optional[str]:
    """Extract the first argument (command name) from a VM command."""
    parts = command.split(" ")
    if len(parts) > 0:
        return parts[0]
    return None


def get_arg1(command: str) -> Optional[str]:
    """Extract the second argument from a VM command."""
    parts = command.split(" ")
    if len(parts) > 1:
        return parts[1]
    return None


def get_arg2(command: str) -> Optional[int]:
    """Extract the third argument (as integer) from a VM command."""
    parts = command.split(" ")
    if len(parts) > 2:
        return int(parts[2])
    return None


def write_array(output: TextIO, instructions: List[str]) -> None:
    """Write an array of assembly instructions to the output file."""
    for instruction in instructions:
        output.write(instruction)
        output.write("\n")


def write_push_asm(output: TextIO) -> None:
    """Write push assembly code to push D register onto stack."""
    write_array(output, PUSH_ASM)


def write_add_asm(output: TextIO) -> None:
    """Write assembly code for add operation."""
    write_array(output, ADD_ASM)


def write_sub_asm(output: TextIO) -> None:
    """Write assembly code for subtract operation."""
    write_array(output, SUB_ASM)


def write_neg_asm(output: TextIO) -> None:
    """Write assembly code for negate operation."""
    write_array(output, NEG_ASM)


def write_eq_asm(output: TextIO, label_index: int) -> None:
    """Write assembly code for equality comparison."""
    eq_asm = [
        "@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D-M",
        f"@TRUE{label_index}", "D;JEQ", "@SP", "A=M-1", "M=0",
        f"@END{label_index}", "0;JMP", f"(TRUE{label_index})",
        "@SP", "A=M-1", "M=-1", f"(END{label_index})"
    ]
    write_array(output, eq_asm)


def write_gt_asm(output: TextIO, label_index: int) -> None:
    """Write assembly code for greater-than comparison."""
    gt_asm = [
        "@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D-M",
        f"@TRUE{label_index}", "D;JGT", "@SP", "A=M-1", "M=0",
        f"@END{label_index}", "0;JMP", f"(TRUE{label_index})",
        "@SP", "A=M-1", "M=-1", f"(END{label_index})"
    ]
    write_array(output, gt_asm)


def write_lt_asm(output: TextIO, label_index: int) -> None:
    """Write assembly code for less-than comparison."""
    lt_asm = [
        "@SP", "M=M-1", "@SP", "A=M-1", "D=M", "@SP", "A=M", "D=D-M",
        f"@TRUE{label_index}", "D;JLT", "@SP", "A=M-1", "M=0",
        f"@END{label_index}", "0;JMP", f"(TRUE{label_index})",
        "@SP", "A=M-1", "M=-1", f"(END{label_index})"
    ]
    write_array(output, lt_asm)


def write_and_asm(output: TextIO) -> None:
    """Write assembly code for bitwise AND operation."""
    write_array(output, AND_ASM)


def write_or_asm(output: TextIO) -> None:
    """Write assembly code for bitwise OR operation."""
    write_array(output, OR_ASM)


def write_not_asm(output: TextIO) -> None:
    """Write assembly code for bitwise NOT operation."""
    write_array(output, NOT_ASM)


def write_push_item(output: TextIO, command: str, filename: str) -> None:
    """
    Write assembly code to load a value into D register for pushing onto stack.

    Args:
        output: The output file handle.
        command: The push command.
        filename: The base filename (used for static variables).
    """
    arg1 = get_arg1(command)
    arg2 = get_arg2(command)

    if arg1 == "constant":
        output.write(f"@{arg2}\n")
        output.write("D=A\n")
    elif arg1 == "argument":
        write_array(output, [f"@{arg2}", "D=A", "@ARG", "A=M+D", "D=M"])
    elif arg1 == "local":
        write_array(output, [f"@{arg2}", "D=A", "@LCL", "A=M+D", "D=M"])
    elif arg1 == "this":
        write_array(output, [f"@{arg2}", "D=A", "@THIS", "A=M+D", "D=M"])
    elif arg1 == "that":
        write_array(output, [f"@{arg2}", "D=A", "@THAT", "A=M+D", "D=M"])
    elif arg1 == "static":
        write_array(output, [f"@{filename}.{arg2}", "D=M"])
    elif arg1 == "pointer":
        write_array(output, [f"@{arg2}", "D=A", "@THIS", "A=A+D", "D=M"])
    elif arg1 == "temp":
        write_array(output, [f"@{arg2}", "D=A", "@5", "A=A+D", "D=M"])


def write_pop_asm(output: TextIO, command: str, filename: str) -> None:
    """
    Write assembly code for pop operation.

    Args:
        output: The output file handle.
        command: The pop command.
        filename: The base filename (used for static variables).
    """
    arg1 = get_arg1(command)
    arg2 = get_arg2(command)

    if arg1 != "static":
        write_array(output, ["@SP", "A=M-1", "D=M", "@R15", "M=D", f"@{arg2}", "D=A"])

    if arg1 == "constant":
        output.write(f"@{arg2}\n")
        output.write("M=D\n")
    elif arg1 == "argument":
        write_array(output, ["@ARG"])
    elif arg1 == "local":
        write_array(output, ["@LCL"])
    elif arg1 == "this":
        write_array(output, ["@THIS"])
    elif arg1 == "that":
        write_array(output, ["@THAT"])
    elif arg1 == "static":
        write_array(output, ["@SP", "A=M-1", "D=M", f"@{filename}.{arg2}", "M=D"])
    elif arg1 == "pointer":
        write_array(output, ["@THIS", "D=A+D"])
    elif arg1 == "temp":
        write_array(output, ["@5", "D=A+D"])

    pop_end = ["D=M+D", "@R14", "M=D", "@R15", "D=M", "@R14", "A=M", "M=D", "@SP", "M=M-1"]

    if arg1 == "pointer" or arg1 == "temp":
        write_array(output, ["@R14", "M=D", "@R15", "D=M", "@R14", "A=M", "M=D", "@SP", "M=M-1"])
    elif arg1 == "static":
        write_array(output, ["@SP", "M=M-1"])
    else:
        write_array(output, pop_end)


def write_push_memory(output: TextIO, segment: str) -> None:
    """Write assembly code to push a memory segment value onto stack."""
    write_array(output, [f"@{segment}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"])


def write_init(output: TextIO) -> None:
    """Write bootstrap code to initialize SP and call Sys.init."""
    init_array = ["@256", "D=A", "@SP", "M=D"]
    write_array(output, init_array)
    write_call(output, "Sys.init", 0, 0)


def write_label(output: TextIO, current_function: str, label: str) -> None:
    """Write assembly code for a label within a function."""
    write_array(output, [f"({current_function}${label})"])


def write_label_function(output: TextIO, label: str) -> None:
    """Write assembly code for a function label."""
    write_array(output, [f"({label})"])


def write_goto(output: TextIO, current_function: str, label: str) -> None:
    """Write assembly code for unconditional goto within a function."""
    write_array(output, [f"@{current_function}${label}", "0;JMP"])


def write_goto_function(output: TextIO, label: str) -> None:
    """Write assembly code for unconditional goto to a function."""
    write_array(output, [f"@{label}", "0;JMP"])


def write_if(output: TextIO, current_function: str, label: str) -> None:
    """Write assembly code for conditional goto within a function."""
    if_array = ["@SP", "M=M-1", "@SP", "A=M", "D=M", f"@{current_function}${label}", "D;JNE"]
    write_array(output, if_array)


def write_if_function(output: TextIO, label: str) -> None:
    """Write assembly code for conditional goto to a function label."""
    if_array = ["@SP", "M=M-1", "@SP", "A=M", "D=M", f"@{label}", "D;JNE"]
    write_array(output, if_array)


def write_call(output: TextIO, function_name: str, num_args: int, label_index: int) -> None:
    """Write assembly code for function call."""
    write_array(output, [f"@return-address{label_index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"])
    write_push_memory(output, "LCL")
    write_push_memory(output, "ARG")
    write_push_memory(output, "THIS")
    write_push_memory(output, "THAT")
    call_array = [
        "@SP", "D=M", "@5", "D=D-A", f"@{num_args}", "D=D-A",
        "@ARG", "M=D", "@SP", "D=M", "@LCL", "M=D"
    ]
    write_array(output, call_array)
    write_goto_function(output, function_name)
    write_label_function(output, f"return-address{label_index}")


def write_return(output: TextIO) -> None:
    """Write assembly code for function return."""
    return_array = [
        "@LCL", "D=M", "@R13", "M=D",
        "@5", "A=D-A", "D=M", "@R14", "M=D",
        "@SP", "A=M-1", "D=M", "@ARG", "A=M", "M=D",
        "@SP", "M=M-1",
        "@ARG", "D=M+1", "@SP", "M=D",
        "@R13", "A=M-1", "D=M", "@THAT", "M=D",
        "@R13", "A=M-1", "A=A-1", "D=M", "@THIS", "M=D",
        "@R13", "A=M-1", "A=A-1", "A=A-1", "D=M", "@ARG", "M=D",
        "@R13", "A=M-1", "A=A-1", "A=A-1", "A=A-1", "D=M", "@LCL", "M=D",
        "@R14", "A=M", "0;JMP"
    ]
    write_array(output, return_array)


def write_function(output: TextIO, function_name: str, num_locals: int) -> None:
    """Write assembly code for function definition."""
    write_label_function(output, function_name)
    for _ in range(num_locals):
        write_array(output, ["@0", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"])


def process_command(
    output: TextIO,
    command: str,
    filename: str,
    current_function: str,
    label_index: int
) -> tuple[str, int]:
    """
    Process a single VM command and write corresponding assembly code.

    Args:
        output: The output file handle.
        command: The VM command to process.
        filename: The base filename (used for static variables).
        current_function: The current function name for label scoping.
        label_index: The current label index for unique labels.

    Returns:
        A tuple of (updated current_function, updated label_index).
    """
    arg1 = get_arg1(command)
    arg2 = get_arg2(command)
    command_type = get_command_type(command)

    if command_type == "C_PUSH":
        write_push_item(output, command, filename)
        write_push_asm(output)
    elif command_type == "C_ARITHMETIC":
        if "add" in command:
            write_add_asm(output)
        elif "sub" in command:
            write_sub_asm(output)
        elif "neg" in command:
            write_neg_asm(output)
        elif "eq" in command:
            write_eq_asm(output, label_index)
            label_index += 1
        elif "gt" in command:
            write_gt_asm(output, label_index)
            label_index += 1
        elif "lt" in command:
            write_lt_asm(output, label_index)
            label_index += 1
        elif "and" in command:
            write_and_asm(output)
        elif "or" in command:
            write_or_asm(output)
        elif "not" in command:
            write_not_asm(output)
    elif command_type == "C_POP":
        write_pop_asm(output, command, filename)
    elif command_type == "C_GOTO":
        write_goto(output, current_function, arg1)
    elif command_type == "C_IF":
        write_if(output, current_function, arg1)
    elif command_type == "C_RETURN":
        write_return(output)
    elif command_type == "C_CALL":
        write_call(output, arg1, arg2, label_index)
        label_index += 1
    elif command_type == "C_FUNCTION":
        current_function = arg1
        write_function(output, arg1, arg2)
    elif command_type == "C_LABEL":
        write_label(output, current_function, arg1)

    return current_function, label_index


def parse_vm_file(filepath: str) -> List[str]:
    """
    Parse a VM file and return a list of cleaned commands.

    Args:
        filepath: Path to the VM file.

    Returns:
        A list of VM commands with comments and whitespace removed.
    """
    commands = []
    with open(filepath) as f:
        for line in f:
            line = line.split("//", 1)[0]
            line = line.strip()
            if line:
                commands.append(line)
    return commands


def main() -> None:
    """Main entry point for the VM translator."""
    directory_name = sys.argv[1]
    real_path = str(Path(sys.argv[1]).resolve())

    init_vm = False
    if sys.argv[1].endswith(".vm"):
        real_path = str(real_path.rpartition("/")[0])
        os.chdir(real_path)
    else:
        os.chdir(os.path.realpath(directory_name))
        init_vm = True

    asm_filename = str(os.getcwd()).rpartition("/")[2]

    items = os.listdir(".")
    vm_files = [item for item in items if item.endswith(".vm")]

    with open(f"{asm_filename}.asm", "w") as output:
        if init_vm:
            write_init(output)

        for vm_file in vm_files:
            commands = parse_vm_file(vm_file)
            base_filename = vm_file[:vm_file.index(".")]

            label_index = 2
            current_function = "main"

            for command in commands:
                current_function, label_index = process_command(
                    output, command, base_filename, current_function, label_index
                )


if __name__ == "__main__":
    main()
