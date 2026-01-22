import logging
from pathlib import Path
from typing import List, Union

from crossfit.models import CommandResult, ReportFormat, ToolType
from crossfit.tools.tool import Tool


class DotnetCoverage(Tool):
    TOOL_TYPE = ToolType.DotnetCoverage

    def snapshot_coverage(self, session, target_dir, target_file,
                          *extras: Union[str, tuple[str, str]]) -> CommandResult:
        """
        Triggers dotnet-coverage agent to save cobertura formatted coverage files to given path.
        :param session: Session id of the wanted dotnet-coverage agent collected-coverage to snapshot.
        :param target_dir: Targeted directory to save dotnet-coverage collection to.
        :param target_file: Specified snapshot file name - when not given - cross-dotnetcoverage.xml.
        :param extras: Extra options to pass to the dotnet-coverage CLI's report command.
        :return: The result of the dump command execution.
        """
        target_path = Path(target_dir) / (
            target_file if target_file is not None else self._get_default_target_filename())
        if not target_path.suffix: target_path = target_path.with_suffix(".xml")
        extras += ("--output", str(target_path)),
        command = (self._get_command("snapshot", extras=extras)
                   .add_command_arguments(session))

        result = self._execute(command)
        return CommandResult(code=result.returncode, error=result.stderr, output=result.stdout, target=str(target_path),
                             command=str(command))

    def merge_coverage(self, coverage_files, target_dir, target_file,
                       *extras: Union[str, tuple[str, str]]) -> CommandResult:
        """
        Merges coverage files into target path of one unified coverage file. Can get extra arguments
        which are supported by the dotnet-coverage CLI.
        """
        extras += ("--output", str(Path(target_dir) / (target_file if target_file is not None else
                                                       self._get_default_target_filename().with_suffix(".xml"))))
        command = self._get_command("merge", command_path_arguments=coverage_files, extras=extras)
        if {"--output-format", "-f"}.intersection(command.command):  # If target file format is not given to command
            command = command.add_option("--output-format", ReportFormat.Cobertura.value.lower())

        result = self._execute(command)
        return CommandResult(code=result.returncode, error=result.stderr, output=result.stdout, target=target_dir,
                             command=str(command))

    def save_report(self, coverage_files: List[str], target_dir: str, sourcecode_dir: str,
                    report_format: ReportFormat = None, report_formats: List[ReportFormat] = None,
                    build_dir: str = None, *extras: Union[str, tuple[str, str]]) -> CommandResult:
        """
        Creates DotnetCoverage report from coverage files to given path.
        :param coverage_files: File paths (can handle wildcards) to create dotnet-coverage report from.
        :param target_dir: Targeted directory to create dotnet coverage report to.
        :param sourcecode_dir: Directory containing the covered sourcecode files.
        :param report_format: Format of dotnet coverage report - :FormatType
        :param report_formats: Multiple formats of dotnet coverage report to create.
        :param extras: extra options to pass to the dotnet CLI's report command.
        :return: The result of the report command execution.
        """
        multiple_values_delimiter = ';'
        if sourcecode_dir: extras += ("-sourcedirs", sourcecode_dir),
        extras += ("-targetdir", target_dir),
        command = (
            self._get_command("", tool=ToolType.DotnetReportGenerator, extras=extras)
            .set_values_delimiter(":", replace_existing_values=True)
            .add_option("-reports", f"\"{multiple_values_delimiter.join(coverage_files)}\""))
        report_formats = set((report_formats or []) + [report_format])
        command = command.add_option("-reporttypes",
                                     f"\"{multiple_values_delimiter.join([rf.value for rf in report_formats if rf])}\"")

        # Ensure different syntax of dotnet-reportgenerator is set to the command's flags
        command.command = [kw.replace("--", "-") for kw in command.command[2:]]
        result = self._execute(command)
        return CommandResult(code=result.returncode, error=result.stderr, output=result.stdout, target=target_dir,
                             command=str(command))

    def __init__(self, tool_path: str, logger: logging.Logger = None, catch: bool = True, **execution_arguments):
        super().__init__(tool_path, logger, catch, **execution_arguments)
