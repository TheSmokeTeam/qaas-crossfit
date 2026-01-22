# test_tool.py
import pytest

import tests
from crossfit.tools.tool import Tool
import subprocess
from crossfit.commands.command import Command


class TestTool(Tool):
    def save_report(self, coverage_files, target_dir, report_format, report_formats, sourcecode_dir, *extras):
        pass

    def snapshot_coverage(self, session, target_dir, target_file, *extras):
        pass

    def merge_coverage(self, coverage_files, target_dir, target_file, *extras):
        pass

    def reset_coverage(self, session, *extras):
        pass

    def __init__(self, tool_path, logger, catch, **kwargs):
        super(TestTool, self).__init__(tool_path, logger, catch, **kwargs)


@pytest.fixture
def tool():
    return TestTool(r"./", tests.logger, False, **{"check": True})


def test_tool_execute_with_non_existing_tool(tool):
    command = Command(["oc.exercise", "/c", "echo", "hello"])
    with pytest.raises(FileNotFoundError):
        tool._execute(command)


def test_tool_execute_success(tool, monkeypatch):
    command = Command(["echo", "hello"])

    def mock_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode=0)

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = tool._execute(command)
    assert result.returncode == 0


def test_tool_execute_failure_not_caught(tool, monkeypatch):
    command = Command(["echo", "hello"])

    def mock_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode=312, stderr="")

    monkeypatch.setattr(subprocess, 'run', mock_run)
    with pytest.raises(subprocess.CalledProcessError):
        tool._execute(command)


def test_tool_execute_failure_not_caught_only_error_message(tool, monkeypatch):
    command = Command(["echo", "hello"])

    def mock_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode=0, stderr="error message")

    monkeypatch.setattr(subprocess, 'run', mock_run)
    with pytest.raises(subprocess.CalledProcessError):
        tool._execute(command)
