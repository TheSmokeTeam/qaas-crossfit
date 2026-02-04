import pytest
import subprocess
import shutil
import os
from pathlib import Path
from crossfit import DotnetCoverage, Command
from crossfit.executors import LocalExecutor
from crossfit.models import CommandResult, ReportFormat

# Path where global dotnet tools are installed
DOTNET_TOOLS_PATH = os.path.expanduser("~/.dotnet/tools")


def _get_dotnet_path():
    """Find dotnet executable in PATH or common installation locations."""
    # First try to find dotnet in PATH
    dotnet_in_path = shutil.which("dotnet")
    if dotnet_in_path:
        return dotnet_in_path

    # Fallback to common installation paths
    common_paths = [
        "/usr/local/share/dotnet/dotnet",  # macOS
        "/usr/share/dotnet/dotnet",         # Linux
        "/usr/bin/dotnet",                  # Linux alternative
    ]
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    raise RuntimeError("dotnet executable not found. Please install .NET SDK.")


def _get_dotnet_major_version(dotnet_path):
    """Get the major version of the .NET SDK."""
    try:
        result = subprocess.run([dotnet_path, "--version"], capture_output=True, text=True, check=True)
        version_str = result.stdout.strip()
        major_version = int(version_str.split('.')[0])
        return major_version
    except Exception:
        return None


def _get_tool_versions(dotnet_path):
    """Get compatible tool versions based on .NET SDK version."""
    major_version = _get_dotnet_major_version(dotnet_path)

    # For .NET 7 or older, use older compatible versions
    if major_version is not None and major_version < 8:
        return {
            "dotnet-coverage": "17.13.0",
            "dotnet-reportgenerator-globaltool": "5.2.5"
        }
    # For .NET 8+, let dotnet choose the latest compatible versions
    return None


@pytest.fixture(scope="module")
def install_dotnet_tools():
    """Install required dotnet tools before tests and uninstall after."""
    dotnet_path = _get_dotnet_path()
    tool_versions = _get_tool_versions(dotnet_path)

    # Install the tools
    if tool_versions:
        subprocess.run([dotnet_path, "tool", "install", "--global", "dotnet-coverage",
                       "--version", tool_versions["dotnet-coverage"]], check=False)
        subprocess.run([dotnet_path, "tool", "install", "--global", "dotnet-reportgenerator-globaltool",
                       "--version", tool_versions["dotnet-reportgenerator-globaltool"]], check=False)
    else:
        subprocess.run([dotnet_path, "tool", "install", "--global", "dotnet-coverage"], check=False)
        subprocess.run([dotnet_path, "tool", "install", "--global", "dotnet-reportgenerator-globaltool"], check=False)

    yield

    # Cleanup: uninstall the tools after tests
    subprocess.run([dotnet_path, "tool", "uninstall", "--global", "dotnet-coverage"], check=False)
    subprocess.run([dotnet_path, "tool", "uninstall", "--global", "dotnet-reportgenerator-globaltool"], check=False)


@pytest.fixture
def dotnetcoverage_tool(logger, install_dotnet_tools):
    return DotnetCoverage(logger, catch=True)


@pytest.fixture
def local_executor(logger, install_dotnet_tools):
    # Add dotnet tools directory to PATH for subprocess execution
    env = os.environ.copy()
    env["PATH"] = f"{DOTNET_TOOLS_PATH}:{env.get('PATH', '')}"
    return LocalExecutor(logger, False, **{"check": True, "env": env})


@pytest.fixture
def coverage_files(tests_dir_path):
    return [Path(tests_dir_path / r"helpers/tools/dotnetcoverage/s1.cobertura.xml"),
            Path(tests_dir_path / r"helpers/tools/dotnetcoverage/s2.cobertura.xml")]


@pytest.fixture
def target_dir(tests_dir_path):
    return Path(tests_dir_path / r"helpers/tools/dotnetcoverage/output/")


@pytest.fixture
def sourcecode_dir(tests_dir_path):
    return Path(tests_dir_path / r"helpers/tools/dotnetcoverage/sourcecode/")


@pytest.mark.parametrize("report_format, report_formats, expected_return_code", [
    (None, [ReportFormat.Html, ReportFormat.Xml], 0),
    (ReportFormat.Html, None, 0),
    (ReportFormat.Xml, [], 0),
], ids=[
    "Csv_Report_With_Html_And_Xml",
    "Html_Report",
    "Xml_Report_Only",
])
def test_dotnetcoverage_execute_report(dotnetcoverage_tool, local_executor, coverage_files, target_dir, sourcecode_dir,
                                       report_format, report_formats, expected_return_code):
    command = dotnetcoverage_tool.save_report(
        coverage_files, target_dir, sourcecode_dir, report_format, report_formats)

    assert isinstance(command, Command)

    result = local_executor.execute(command)
    assert isinstance(result, CommandResult)
    assert result.code == expected_return_code


def test_dotnetcoverage_merge_coverage(dotnetcoverage_tool, local_executor, coverage_files, target_dir):
    target_file = Path("merged")

    command = dotnetcoverage_tool.merge_coverage(coverage_files, target_dir, target_file)
    assert isinstance(command, Command)

    result = local_executor.execute(command)
    assert isinstance(result, CommandResult)
    assert result.code == 0
