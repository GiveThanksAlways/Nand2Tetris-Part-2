"""
VM Writer module for the Jack compiler.

This module provides functionality for writing VM code output,
translating high-level constructs to Hack VM commands.
"""

from typing import Union


class VMWriter:
    """Writes VM commands to an output file."""

    def __init__(self, vm_output_path: str) -> None:
        """
        Initialize the VM writer with an output file.

        Args:
            vm_output_path: Path for the output VM file (without extension).
        """
        self.output = open(f'{vm_output_path}.vm', 'w')

    def write_push(self, segment: str, index: Union[int, str]) -> None:
        """
        Write a VM push command.

        Args:
            segment: The memory segment to push from.
            index: The index within the segment.
        """
        if segment is not None and index is not None:
            self.output.write(f'push {segment} {index}\n')

    def write_pop(self, segment: str, index: Union[int, str]) -> None:
        """
        Write a VM pop command.

        Args:
            segment: The memory segment to pop to.
            index: The index within the segment.
        """
        if segment is not None and index is not None:
            self.output.write(f'pop {segment} {index}\n')

    def write_arithmetic(self, command: str) -> None:
        """
        Write a VM arithmetic command.

        Args:
            command: The arithmetic operation (+, -, *, /, etc.).
        """
        wrote_command = True

        if command == '+':
            self.output.write('add')
        elif command == '-':
            self.output.write('sub')
        elif command == 'NEG':
            self.output.write('neg')
        elif command == '=':
            self.output.write('eq')
        elif command == '&gt;':
            self.output.write('gt')
        elif command == '&lt;':
            self.output.write('lt')
        elif command == '&amp;':
            self.output.write('and')
        elif command == '|':
            self.output.write('or')
        elif command == 'NOT':
            self.output.write('not')
        elif command == '^':
            self.write_call('Math.power', 2)
            wrote_command = False
        elif command == '*':
            self.write_call('Math.multiply', 2)
            wrote_command = False
        elif command == '/':
            self.write_call('Math.divide', 2)
            wrote_command = False
        elif command == '~':
            self.output.write('not')
        else:
            wrote_command = False

        if wrote_command:
            self.output.write('\n')

    def write_label(self, label: str) -> None:
        """
        Write a VM label command.

        Args:
            label: The label name.
        """
        self.output.write(f'label {label}\n')

    def write_goto(self, label: str) -> None:
        """
        Write a VM goto command.

        Args:
            label: The target label name.
        """
        self.output.write(f'goto {label}\n')

    def write_if(self, label: str) -> None:
        """
        Write a VM if-goto command.

        Args:
            label: The target label name.
        """
        self.output.write(f'if-goto {label}\n')

    def write_call(self, name: str, num_args: int) -> None:
        """
        Write a VM call command.

        Args:
            name: The function name to call.
            num_args: The number of arguments.
        """
        if num_args == 0:
            self.output.write(f'call {name}\n')
        else:
            self.output.write(f'call {name} {num_args}\n')

    def write_function(self, class_name: str, name: str, num_locals: int) -> None:
        """
        Write a VM function declaration.

        Args:
            class_name: The class name.
            name: The function name.
            num_locals: The number of local variables.
        """
        self.output.write(f'function {class_name}.{name} {num_locals}\n')

    def write_return(self) -> None:
        """Write a VM return command."""
        self.output.write('return\n')
