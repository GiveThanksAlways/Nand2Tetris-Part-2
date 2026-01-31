"""
VM Writer - Generates VM code for the Jack compiler.

Writes VM commands to output file during compilation.
Part of the Nand2Tetris course (Project 11).
"""

from typing import Union


class VMWriter:
    """Writes VM commands to an output file."""

    def __init__(self, vm_output_path: str) -> None:
        """Initialize VMWriter with output file path."""
        self.output = open(f"{vm_output_path}.vm", 'w')

    def write_push(self, segment: str, index: Union[int, str]) -> None:
        """Write a VM push command."""
        if segment is not None and index is not None:
            self.output.write(f"push {segment} {index}\n")

    def write_pop(self, segment: str, index: Union[int, str]) -> None:
        """Write a VM pop command."""
        if segment is not None and index is not None:
            self.output.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, command: str) -> None:
        """Write a VM arithmetic command."""
        # Map operators to VM commands
        operator_map = {
            '+': 'add',
            '-': 'sub',
            'NEG': 'neg',
            '=': 'eq',
            '&gt;': 'gt',
            '&lt;': 'lt',
            '&amp;': 'and',
            '|': 'or',
            'NOT': 'not',
            '~': 'not'  # Boolean negation
        }

        if command in operator_map:
            self.output.write(f"{operator_map[command]}\n")
        elif command == '^':
            self.write_call('Math.power', 2)
        elif command == '*':
            self.write_call('Math.multiply', 2)
        elif command == '/':
            self.write_call('Math.divide', 2)

    def write_label(self, label: str) -> None:
        """Write a VM label command."""
        self.output.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        """Write a VM goto command."""
        self.output.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        """Write a VM if-goto command."""
        self.output.write(f"if-goto {label}\n")

    def write_call(self, name: str, num_args: int) -> None:
        """Write a VM call command."""
        if num_args == 0:
            self.output.write(f"call {name}\n")
        else:
            self.output.write(f"call {name} {num_args}\n")

    def write_function(self, class_name: str, function_name: str, num_locals: int) -> None:
        """Write a VM function command."""
        self.output.write(f"function {class_name}.{function_name} {num_locals}\n")

    def write_return(self) -> None:
        """Write a VM return command."""
        self.output.write("return\n")

    # Backward compatibility aliases
    def writePush(self, segment: str, index: Union[int, str]) -> None:
        self.write_push(segment, index)

    def writePop(self, segment: str, index: Union[int, str]) -> None:
        self.write_pop(segment, index)

    def writeArithmetic(self, command: str) -> None:
        self.write_arithmetic(command)

    def writeLabel(self, label: str) -> None:
        self.write_label(label)

    def writeGoto(self, label: str) -> None:
        self.write_goto(label)

    def writeIf(self, label: str) -> None:
        self.write_if(label)

    def writeCall(self, name: str, num_args: int) -> None:
        self.write_call(name, num_args)

    def writeFunction(self, class_name: str, function_name: str, num_locals: int) -> None:
        self.write_function(class_name, function_name, num_locals)

    def writeReturn(self) -> None:
        self.write_return()
