import os.path
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
    return [str(os.path.relpath(tests_dir_path / r"tests_helpers/tools/jacoco/f1.exec")),
            str(os.path.relpath(tests_dir_path / r"tests_helpers/tools/jacoco/f2.exec"))]


@pytest.fixture
def target_dir():
    return str(os.path.relpath(tests_dir_path / r"tests_helpers/tools/jacoco/output/"))


@pytest.fixture
def sourcecode_dir():
    return str(os.path.relpath(tests_dir_path / r"tests_helpers/tools/jacoco/sourcecode/"))


@pytest.fixture
def classfiles_dir():
    return str(os.path.relpath(tests_dir_path / r"tests_helpers/tools/jacoco/classfiles/"))


@pytest.mark.parametrize("report_format, report_formats, expected_return_code", [
    (ReportFormat.Csv, [ReportFormat.Html, ReportFormat.Xml], 0),
    (ReportFormat.Html, None, 0),
    (ReportFormat.Xml, [], 0),
], ids=[
    "Csv_Report_With_Html_And_Xml",
    "Html_Report",
    "Xml_Report_Only",
])
def test_jacoco_execute_report(jacoco_tool, coverage_files, target_dir, sourcecode_dir, classfiles_dir,
                               report_format, report_formats, expected_return_code):
    extras = ["--quiet", ("--tabwith", "6")]

    result = jacoco_tool.save_report(coverage_files, target_dir, sourcecode_dir, report_format, report_formats,
                                     classfiles_dir, *extras)
    assert isinstance(result, CommandResult)
    assert result.code == expected_return_code


def test_jacoco_execute_report_files_wildcard(jacoco_tool, target_dir, sourcecode_dir, classfiles_dir):
    report_format = ReportFormat.Csv
    coverage_files = [str(tests_dir_path / r"tests_helpers/tools/jacoco/*.exec")]
    report_formats = [ReportFormat.Html, ReportFormat.Xml]
    extras = ["--quiet", ("--tabwith", "6")]

    result = jacoco_tool.save_report(coverage_files, target_dir, sourcecode_dir, report_format, report_formats,
                                     classfiles_dir, *extras)
    assert isinstance(result, CommandResult)
    assert result.code == 0


def test_jacoco_merge_coverage(jacoco_tool, coverage_files, target_dir):
    target_file = "merged.exec"
    extras = []

    result = jacoco_tool.merge_coverage(coverage_files, target_dir, target_file, *extras)
    assert isinstance(result, CommandResult)
    assert result.code == 0
