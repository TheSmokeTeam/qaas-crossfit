import subprocess

import pytest

import crossfit
from crossfit import DotnetCoverage
from crossfit.models import CommandResult, ReportFormat
from tests import logger, tests_dir_path


@pytest.fixture
def dotnetcoverage_tool():
    return DotnetCoverage(crossfit.refs.tools_dir, logger=logger, catch=True)


@pytest.fixture
def coverage_files():
    return [str(tests_dir_path / r"tests_helpers/tools/dotnetcoverage/s1.cobertura.xml"),
            str(tests_dir_path / r"tests_helpers/tools/dotnetcoverage/s2.cobertura.xml")]


@pytest.fixture
def target_dir():
    return str(tests_dir_path / r"tests_helpers/tools/dotnetcoverage/output/")


@pytest.fixture
def sourcecode_dir():
    return str(tests_dir_path / r"tests_helpers/tools/dotnetcoverage/sourcecode/")


@pytest.mark.usefixtures("monkeypatch")
def test_dotnetcoverage_execute_report(monkeypatch, dotnetcoverage_tool, coverage_files, target_dir, sourcecode_dir):
    report_format = ReportFormat.Csv
    report_formats = [ReportFormat.Html, ReportFormat.Xml]
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(dotnetcoverage_tool, "_execute", lambda command: result)

    result = dotnetcoverage_tool.save_report(coverage_files, target_dir, sourcecode_dir, report_format, report_formats)
    assert isinstance(result, CommandResult)
    assert result.code == 0


@pytest.mark.usefixtures("monkeypatch")
def test_dotnetcoverage_merge_coverage(monkeypatch, dotnetcoverage_tool, coverage_files, target_dir):
    target_file = "merged"
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(dotnetcoverage_tool, "_execute", lambda command: result)

    result = dotnetcoverage_tool.merge_coverage(coverage_files, target_dir, target_file)
    assert isinstance(result, CommandResult)
    assert result.code == 0


@pytest.mark.usefixtures("monkeypatch")
def test_dotnetcoverage_snapshot_coverage_with_mocked_execute(monkeypatch, dotnetcoverage_tool):
    session = "dummy_session"
    target_dir = "dummy_dir"
    target_file = "snapshot.exec"
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(dotnetcoverage_tool, "_execute", lambda command: result)

    result = dotnetcoverage_tool.snapshot_coverage(session, target_dir, target_file)
    assert isinstance(result, CommandResult)
    assert result.code == 0


@pytest.mark.usefixtures("monkeypatch")
def test_dotnetcoverage_reset_coverage_with_mocked_execute(monkeypatch, dotnetcoverage_tool):
    session = "dummy_session"
    result = subprocess.CompletedProcess(args=[], returncode=0)
    monkeypatch.setattr(dotnetcoverage_tool, "_execute", lambda command: result)

    result = dotnetcoverage_tool.reset_coverage(session)
    assert isinstance(result, CommandResult)
    assert result.code == 0
