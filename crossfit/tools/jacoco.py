import os.path
from pathlib import Path
from typing import Collection, Optional, Tuple


from crossfit import Command
from crossfit.commands.command_builder import CommandBuilder
from crossfit.models.tool_models import ReportFormat, ToolType
from crossfit.tools.tool import Tool


class Jacoco(Tool):
    _tool_type = ToolType.Jacoco

    def _create_command_builder(self, command, tool_type = None, path_arguments = None, required_flags = None,
                                *extras: Tuple[str, Optional[str]]) -> CommandBuilder:
        tool_type = tool_type or self._tool_type
        command_builder = (super()._create_command_builder(command, tool_type, path_arguments, *extras)
                           .set_execution_call(f"java -jar {os.path.relpath(Path(self._path) / str(tool_type.value))}"))

        required_flags = required_flags or []
        for required_flag in required_flags:
            if required_flag not in [extra[0] for extra in list(extras)]:
                msg = (f"Encountered error while building {tool_type.name} command. "
                       f"JaCoCo flag option {required_flag} is required for command '{command}'.")
                self._logger.error(msg)
                if not self._catch: raise ValueError(msg)
                command_builder.set_command_body(["--help"])

        return command_builder

    def save_report(self, coverage_files, target_dir, report_format, report_formats, sourcecode_dir, build_dir, *extras)\
            -> Command:
        if sourcecode_dir: extras += ("--sourcefiles", str(sourcecode_dir)),
        if build_dir: extras += ("--classfiles", str(build_dir)),
        command = self._create_command_builder(
            "report", None, coverage_files, ["--classfiles"], *extras)
        report_formats = set((report_formats or []) + [report_format])
        for rf in report_formats:
            if rf == ReportFormat.Html:
                command = command.add_option(f"--{rf.name.lower()}", str(target_dir))
            elif rf is not None:
                command = command.add_option(f"--{rf.name.lower()}",
                                             str((Path(target_dir) / self._get_default_target_filename())
                                                 .with_suffix(f".{rf.value.lower()}")))
        return command.build_command()

    def snapshot_coverage(self, session, target_dir, target_file, *extras) -> Command:
        target_path = Path(target_dir) / (
            target_file if target_file is not None else self._get_default_target_filename())
        if not target_path.suffix: target_path = target_path.with_suffix(".exec")
        extras += ("--destfile", str(target_path)),
        command = self._create_command_builder(
            "dump", None, None, None, *extras)
        return command.build_command()

    def merge_coverage(self, coverage_files, target_dir, target_file, *extras) -> Command:
        target_path = Path(target_dir) / (
            target_file if target_file is not None else self._get_default_target_filename())
        if not target_path.suffix: target_path = target_path.with_suffix(".exec")
        extras += ("--destfile", str(target_path)),
        command = self._create_command_builder(
            "merge", None, coverage_files, None,*extras)
        return command.build_command()
