import subprocess

import pytest

import crossfit
from crossfit import DotnetCoverage
from crossfit.models import CommandResult, ReportFormat
from tests import logger, tests_dir_path


@pytest.fixture
def dotnetcoverage_tool():
    return DotnetCoverage("", logger=logger, catch=True)


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


@pytest.mark.parametrize("report_format, report_formats, expected_return_code", [
    (None, [ReportFormat.Html, ReportFormat.Xml], 0),
    (ReportFormat.Html, None, 0),
    (ReportFormat.Xml, [], 0),
], ids=[
    "Csv_Report_With_Html_And_Xml",
    "Html_Report",
    "Xml_Report_Only",
])
def test_dotnetcoverage_execute_report(dotnetcoverage_tool, coverage_files, target_dir, sourcecode_dir,
                                       report_format, report_formats, expected_return_code):
    result = dotnetcoverage_tool.save_report(coverage_files, target_dir, sourcecode_dir, report_format, report_formats)
    assert isinstance(result, CommandResult)
    assert result.code == expected_return_code


def test_dotnetcoverage_merge_coverage(dotnetcoverage_tool, coverage_files, target_dir):
    target_file = "merged"

    result = dotnetcoverage_tool.merge_coverage(coverage_files, target_dir, target_file)
    assert isinstance(result, CommandResult)
    assert result.code == 0
