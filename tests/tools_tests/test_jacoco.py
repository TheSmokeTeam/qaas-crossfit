import subprocess

import pytest

import crossfit
from crossfit import Jacoco
from crossfit.models import CommandResult, ReportFormat
from tests import logger, tests_dir_path


@pytest.fixture
def jacoco_tool():
    return Jacoco(crossfit.refs.tools_dir, logger=logger, catch=True)


@pytest.fixture
def coverage_files():
    return [str(tests_dir_path / r"tests_helpers/tools/jacoco/f1.exec"),
            str(tests_dir_path / r"tests_helpers/tools/jacoco/f2.exec")]


@pytest.fixture
def target_dir():
    return str(tests_dir_path / r"tests_helpers/tools/jacoco/output/")


@pytest.fixture
def sourcecode_dir():
    return str(tests_dir_path / r"tests_helpers/tools/jacoco/sourcecode/")


@pytest.fixture
def classfiles_dir():
    return str(tests_dir_path / r"tests_helpers/tools/jacoco/classfiles/")


@pytest.mark.usefixtures("monkeypatch")
def test_jacoco_execute_report(monkeypatch, jacoco_tool, coverage_files, target_dir, sourcecode_dir, classfiles_dir):
    report_format = ReportFormat.Csv
    report_formats = [ReportFormat.Html, ReportFormat.Xml]
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(jacoco_tool, "_execute", lambda command: result)

    result = jacoco_tool.save_report(coverage_files, target_dir, sourcecode_dir, report_format, report_formats,
                                     build_dir=classfiles_dir)
    assert isinstance(result, CommandResult)
    assert result.code == 0


@pytest.mark.usefixtures("monkeypatch")
def test_jacoco_merge_coverage(monkeypatch, jacoco_tool, coverage_files, target_dir):
    target_file = "merged.exec"
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(jacoco_tool, "_execute", lambda command: result)

    result = jacoco_tool.merge_coverage(coverage_files, target_dir, target_file)
    assert isinstance(result, CommandResult)
    assert result.code == 0


@pytest.mark.usefixtures("monkeypatch")
def test_jacoco_snapshot_coverage_with_mocked_execute(monkeypatch, jacoco_tool):
    session = "dummy_session"
    target_dir = "dummy_dir"
    target_file = "snapshot.exec"
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(jacoco_tool, "_execute", lambda command: result)

    result = jacoco_tool.snapshot_coverage(session, target_dir, target_file)
    assert isinstance(result, CommandResult)
    assert result.code == 0


@pytest.mark.usefixtures("monkeypatch")
def test_jacoco_reset_coverage_with_mocked_execute(monkeypatch, jacoco_tool):
    session = "dummy_session"
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(jacoco_tool, "_execute", lambda command: result)

    result = jacoco_tool.reset_coverage(session)
    assert isinstance(result, CommandResult)
    assert result.code == 0
