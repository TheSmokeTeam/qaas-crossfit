import itertools
import logging
import os.path
from pathlib import Path
from typing import List, Collection, Union

from crossfit.commands.command import Command
from crossfit.models.command_models import CommandResult
from crossfit.models.tool_models import ReportFormat, ToolType
from crossfit.tools.tool import Tool


class Jacoco(Tool):
    TOOL_TYPE = ToolType.Jacoco

    def _get_command(self, tool_command: str, tool: ToolType = None,
                     command_path_arguments: Collection[Union[str, Path]] = None,
                     extras: Collection[Union[str, tuple[str, str]]] = None,
                     required_flags: Collection[str] = None) -> Command:
        """
        Overrides general command building to validate required options when building a JaCoCo tool's command.
        """
        required_flags = required_flags or []
        tool = tool or self.TOOL_TYPE
        command = (super()._get_command(tool_command, tool, command_path_arguments, extras)
                   .set_tool_execution_call(f"java -jar {os.path.relpath(Path(self.tool_path) / str(tool.value))}"))

        for required_flag in required_flags:
            if (required_flag not in itertools.chain(*[flag for flag in extras if isinstance(flag, tuple)])
                    and required_flag not in extras):
                msg = (f"Encountered error while building {self.TOOL_TYPE.name} command. "
                       f"JaCoCo flag option {required_flag} is required for command '{tool_command}'.")
                self._logger.error(msg)
                if not self._catch: raise ValueError(msg)
                command.command = ["--help"]

        return command

    def save_report(self, coverage_files: List[str], target_dir: str, sourcecode_dir: str = None,
                    report_format: ReportFormat = None, report_formats: List[ReportFormat] = None,
                    build_dir: str = None, *extras: Union[str, tuple[str, str]]) -> CommandResult:
        """
        Creates JaCoCo report from coverage files to given path.
        :param coverage_files: File paths (can handle wildcards) to create JaCoCo coverage report from.
        :param target_dir: Targeted directory to create JaCoCo coverage report to.
        :param sourcecode_dir: Directory containing the covered sourcecode files.
        :param report_format: Format of JaCoCo coverage report - :FormatType
        :param report_formats: Multiple formats of JaCoCo coverage report to create.
        :param extras: extra options to pass to the JaCoCo CLI's report command.
        :param build_dir: Directory containing the Java class files. Required.
        :return: The result of the report command execution.
        """
        if sourcecode_dir: extras += ("--sourcefiles", sourcecode_dir),
        if build_dir: extras += ("--classfiles", build_dir),
        command = self._get_command("report", command_path_arguments=coverage_files,
                                    extras=extras, required_flags=["--classfiles"])
        report_formats = set((report_formats or []) + [report_format])
        for rf in report_formats:
            if rf == ReportFormat.Html:
                command = command.add_option(f"--{rf.name.lower()}", target_dir)
            elif rf is not None:
                command = command.add_option(f"--{rf.name.lower()}",
                                             str((Path(target_dir) / self._get_default_target_filename())
                                                 .with_suffix(f".{rf.value.lower()}")))

        result = self._execute(command)
        return CommandResult(code=result.returncode, error=result.stderr, output=result.stdout, target=target_dir,
                             command=str(command))

    def snapshot_coverage(self, session, target_dir, target_file,
                          *extras: Union[str, tuple[str, str]]) -> CommandResult:
        """
        Triggers JaCoCo agent to save .exec formatted coverage files to given path.
        :param session: Session id of the JaCoCo agent collected coverage to snapshot.
        :param target_dir: Targeted directory to save JaCoCo coverage collection to.
        :param target_file: Specified snapshot file name - when not given - cross-jacoco.exec.
        :param extras: Extra options to pass to the JaCoCo CLI's report command.
        :return: The result of the dump command execution.
        """
        target_path = Path(target_dir) / (
            target_file if target_file is not None else self._get_default_target_filename())
        if not target_path.suffix: target_path = target_path.with_suffix(".exec")
        extras += ("--destfile", str(target_path))
        command = self._get_command("dump", extras=extras)

        result = self._execute(command)
        return CommandResult(code=result.returncode, error=result.stderr, output=result.stdout, target=str(target_path),
                             command=str(command))

    def merge_coverage(self, coverage_files, target_dir, target_file,
                       *extras: Union[str, tuple[str, str]]) -> CommandResult:
        """
        Merges coverage files into target path of one unified coverage file. Can get extra arguments
        which are supported by the JaCoCo CLI.
        """
        target_path = Path(target_dir) / (
            target_file if target_file is not None else self._get_default_target_filename())
        if not target_path.suffix: target_path = target_path.with_suffix(".exec")
        extras += ("--destfile", str(target_path))
        command = self._get_command("merge", command_path_arguments=coverage_files, extras=extras)

        result = self._execute(command)
        return CommandResult(code=result.returncode, error=result.stderr, output=result.stdout, target=target_dir,
                             command=str(command))

    def __init__(self, tool_path: str = None, logger: logging.Logger = None, catch: bool = True, **execution_arguments):
        super().__init__(tool_path, logger, catch, **execution_arguments)
