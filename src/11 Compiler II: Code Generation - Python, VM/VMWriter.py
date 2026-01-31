"""
VM Writer module for the Jack compiler.

This module provides functionality to write VM commands to output files,
translating high-level Jack constructs into VM bytecode.
"""

from typing import Optional, Union


class VMWriter:
    """Writes VM commands to an output file."""

    def __init__(self, output_path: str):
        """
        Initialize the VM writer with an output file.

        Args:
            output_path: Base path for the output .vm file.
        """
        self.output = open(f'{output_path}.vm', 'w')

    def write_push(self, segment: Optional[str],
                   index: Optional[Union[int, str]]) -> None:
        """Write a VM push command."""
        if segment is not None and index is not None:
            self.output.write(f'push {segment} {index}\n')

    def write_pop(self, segment: Optional[str],
                  index: Optional[Union[int, str]]) -> None:
        """Write a VM pop command."""
        if segment is not None and index is not None:
            self.output.write(f'pop {segment} {index}\n')

    def write_arithmetic(self, command: str) -> None:
        """
        Write a VM arithmetic command.

        Args:
            command: The arithmetic operator or command name.
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
        """Write a VM label command."""
        self.output.write(f'label {label}\n')

    def write_goto(self, label: str) -> None:
        """Write a VM goto command."""
        self.output.write(f'goto {label}\n')

    def write_if(self, label: str) -> None:
        """Write a VM if-goto command."""
        self.output.write(f'if-goto {label}\n')

    def write_call(self, name: str, num_args: Union[int, str]) -> None:
        """Write a VM call command."""
        if num_args == 0:
            self.output.write(f'call {name}\n')
        else:
            self.output.write(f'call {name} {num_args}\n')

    def write_function(self, class_name: str, name: str, num_locals: int) -> None:
        """Write a VM function declaration."""
        self.output.write(f'function {class_name}.{name} {num_locals}\n')

    def write_return(self) -> None:
        """Write a VM return command."""
        self.output.write('return\n')

    # Backwards compatibility aliases
    writePush = write_push
    writePop = write_pop
    writeArithmetic = write_arithmetic
    writeLabel = write_label
    writeGoto = write_goto
    writeIf = write_if
    writeCall = write_call
    writeFunction = write_function
    writeReturn = write_return
