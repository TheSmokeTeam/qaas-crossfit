import glob
import os.path
from pathlib import Path
from typing import List, Union

from typeguard import typechecked


class Command:
    _COMMAND_DELIMITER = " "
    _execution_call: Union[str, None] = None
    _command_to_execute: Union[str, None] = None
    _command: List[str]
    _options: List[Union[str, tuple[str, str]]]
    _arguments: List[str]

    @typechecked()
    def __init__(self, command: Union[None, List[str]] = None):
        self._values_delimiter = None
        self._options = []
        self._arguments = []
        if command:
            if len(command) < 2: raise ValueError(
                'Command construct parameter must have at least two str arguments - execution call and any arguments')
            self._execution_call = command[0]
            self._command_to_execute = command[1]
            self._command = command[2:]
        else:
            self._command = []

    @property
    def command(self) -> List[str]:
        """
        :return: Collection of strings to represent the command
        """
        return list(filter(lambda s: s is not None, [self._execution_call, self._command_to_execute, *self._command]))

    @command.setter
    def command(self, value: List[str]):
        """
        Sets the command itself without touching the execution call or the command to execute
        """
        self._options = []
        self._arguments = []
        self._command = value

    def __str__(self):
        """
        :return: String representation of the command as triggered on the machine's terminal
        """
        return self._COMMAND_DELIMITER.join(self.command)

    def validate(self):
        """
        Validates that the commands holds execution body and arguments and fully built
        """
        if not self._execution_call:
            raise AttributeError(f"Ensure tool's execution call is set. Valued as: '{self._execution_call}'")

    @staticmethod
    def __validate_path(path: Path):
        """
        Validates that the path exists and valid
        :param path: The path to validate
        """
        paths = glob.glob(str(path), recursive=True)
        if not paths: raise FileNotFoundError(f"Could not recognize given path - '{path}' - does not exist")

    def set_tool_execution_call(self, tool_execution_call: str, tool_path: Path = None):
        """
        Sets command execution call - in order to call the wanted tool from its path
        :param tool_execution_call: the tool's call keyword :example: JaCoCo - jacococli.jar...
        :param tool_path: path to the tool's execution call keyword :example: JaCoCo - /usr/lib/tools/jacoco/...
        """
        self._execution_call = tool_execution_call if tool_path is None else os.path.relpath(
            tool_path / tool_execution_call)
        return self

    def set_tool_command(self, command_keyword: str):
        """
        Sets the command to execute from the wanted tool
        :param command_keyword: :example: JaCoCo - dump / merge / report...
        """
        self._command_to_execute = command_keyword
        return self

    @typechecked()
    def set_values_delimiter(self, delimiter: Union[str, None], replace_existing_values: bool = False):
        old_delimiter = self._values_delimiter
        if old_delimiter == delimiter: return self
        self._values_delimiter = delimiter
        return self if not replace_existing_values else self.__reset_all_options_in_command()

    def __reset_all_options_in_command(self):
        """
        Updates the option to value delimiter for all the options in the command.
        """
        self._command = self._command[:-sum([len(opt) if isinstance(opt, tuple) else 1 for opt in self._options])]
        options = self._options.copy()
        self._options = []
        self.add_options(*options)
        return self

    @typechecked()
    def __add_option(self, option: str, value: Union[str, None] = None, delimiter: Union[str, None] = None):
        """
        Adds an option to the command (option as flag of the command)
        :param option: the option's keyword
        :param value: the value given to the option (if required)
        :param delimiter: the delimiter between the option and the parameter (syntax dependent)
        """
        if delimiter is not None:
            self._values_delimiter = delimiter

        if value is not None:
            # Use the delimiter if set, otherwise append the option and value separately
            if self._values_delimiter is not None:
                option_with_value = f"{option}{self._values_delimiter}{value}"
                self._command.append(option_with_value)
            else:
                self._command.extend([option, value])
            self._options.append((option, value))
        else:
            # Handle option without value
            self._command.append(option)
            self._options.append(option)

    def add_option(self, option: str, value: str = None, delimiter: str = None):
        """
        Self construct method that calls the add_option method to add flag option
        """
        self.__add_option(option, value, delimiter)
        return self

    def add_options(self, *args: Union[str, tuple[str, str]]):
        """
        Adds multiple flag options to the command
        :param args: options keywords with no values to attach
        """
        for option in args:
            if isinstance(option, tuple):
                if len(option) != 2: raise ValueError(f"Option given {option} supposed to hold two parameters -"
                                                      f" string flag and string value")
                self.__add_option(*option[:2])
            else:
                self.__add_option(option)
        return self

    def add_command_arguments(self, *args):
        """
        Add arguments to the command
        """
        args = list(args)
        self._command = self._command[len(self._arguments):]
        self._arguments.extend(args.copy())
        self._command = self._arguments + self._command
        return self

    def add_command_path_arguments(self, *paths: str):
        """
        Adds multiple paths to the command as arguments
        :param paths: Paths to add
        """
        [self.__validate_path(Path(path)) for path in paths]
        resolved_glob_paths = []
        for path in paths:
            resolved_glob_paths.extend(os.path.relpath(resolved_path) for resolved_path in
                                       glob.glob(str(path), recursive=True))
        return self.add_command_arguments(*[os.path.relpath(path) for path in resolved_glob_paths])

    def __copy__(self):
        return Command().add_command_arguments(*self._arguments).add_options(*self._options).set_tool_command(
            self._command_to_execute).set_tool_execution_call(self._execution_call)
