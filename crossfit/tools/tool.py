import logging
import subprocess
import tempfile
from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from subprocess import CompletedProcess
from typing import Collection, Union

from crossfit.commands.command import Command
from crossfit.models.command_models import CommandResult
from crossfit.models.tool_models import ToolType


class Tool(ABC):
    TOOL_TYPE: ToolType

    def _get_default_target_filename(self):
        return f"cross-{self.TOOL_TYPE.name}".lower()

    def _get_command(self, tool_command: str, tool: ToolType = None,
                     command_path_arguments: Collection[Union[str, Path]] = None,
                     extras: Collection[Union[str, tuple[str, str]]] = None) -> Command:
        """
        Creates the command to run the tool's wanted functionality.
        :param tool_command: The type of the command of the tool to build on.
        :param tool: The tool used to build the command on.
        :param command_path_arguments: Path arguments to add to the command.
        :param extras: extra options to pass to the CLI's command.
        """
        tool = tool or self.TOOL_TYPE
        command_path_arguments = command_path_arguments or []
        extras = extras or []
        command = Command().set_tool_execution_call(str(tool.value), Path(self.tool_path) if self.tool_path else None)
        try:
            return (command.set_tool_command(tool_command)
                    .add_command_path_arguments(*command_path_arguments)
                    .add_options(*extras))
        except FileNotFoundError as e:
            self._logger.error(f"Encountered exception while building {self.TOOL_TYPE.name} command. Error - {e}")
            if not self._catch: raise
            command.command = ["--help"]
            return command

    @abstractmethod
    def save_report(self, coverage_files, target_dir, report_format, report_formats, sourcecode_dir, build_dir,
                    *extras: Union[str, tuple[str, str]]) -> CommandResult:
        raise NotImplemented

    @abstractmethod
    def snapshot_coverage(self, session, target_dir, target_file,
                          *extras: Union[str, tuple[str, str]]) -> CommandResult:
        raise NotImplemented

    @abstractmethod
    def merge_coverage(self, coverage_files, target_dir, target_file,
                       *extras: Union[str, tuple[str, str]]) -> CommandResult:
        raise NotImplemented

    def reset_coverage(self, session, *extras: Union[str, tuple[str, str]]) -> CommandResult:
        tmp_target_dir = Path(tempfile.gettempdir()) / r"crossfit"
        extras += "--reset",
        tmp_execution_res = self.snapshot_coverage(session, tmp_target_dir, None, *extras)

        cleaning_command = Command(["rm", "-f", str(tmp_target_dir)])
        cleaning_res = self._execute(cleaning_command)
        return tmp_execution_res.add_result(CommandResult(code=cleaning_res.returncode, error=cleaning_res.stderr,
                                                          output=cleaning_res.stdout, target=str(tmp_target_dir),
                                                          command=str(cleaning_command)))

    def __init__(self, tool_path: Union[str, None], logger: logging.Logger, catch: bool = True, **execution_arguments):
        """
        :param tool_path: The path called in the command to execute the tool.
        :param catch: Catch or re-raise the exception.
        :param execution_arguments: Additional or updated arguments for the command executor that
        may affect the command execution.
        """
        self.tool_path: Union[str, None] = tool_path
        self._exec_kwargs: dict = {
            "capture_output": True,
            "check": True,
            "text": True,
        }
        self._exec_kwargs.update(execution_arguments)
        self._logger: Logger = logger
        self._catch: bool = catch

    def _execute(self, command: Command) -> CompletedProcess:
        try:
            command.validate()
            res = subprocess.run(str(command), **(self._exec_kwargs if self._exec_kwargs else {}))
            if res.returncode != 0 or (res.stderr and len(res.stderr)):
                raise subprocess.CalledProcessError(res.returncode, str(command), output=res.stdout,
                                                    stderr=res.stderr)
            self._logger.info(f"Command '{command}' finished with exit code {res.returncode}. {res.stdout}")
            return res
        except subprocess.CalledProcessError as cpe:
            self._logger.error(
                f"Execution of command '{str(command)}' failed with error: {cpe.stderr}. Return code {cpe.returncode}.")
            if not self._catch: raise
            return CompletedProcess(args=cpe.args, stderr=cpe.stderr, returncode=cpe.returncode, stdout=cpe.stdout)
        except FileNotFoundError as not_found_e:
            self._logger.error(f"Command '{str(command)}' not found. {not_found_e.strerror}")
            if not self._catch: raise
            return CompletedProcess(str(command), returncode=127, stderr=not_found_e.strerror)
        except Exception as e:
            self._logger.error(f"An error occurred while executing command '{str(command)}': {e}")
            if not self._catch: raise
            return CompletedProcess(str(command), returncode=1, stderr=str(e))
