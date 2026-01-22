import os.path

import pytest
from typeguard import TypeCheckError

from crossfit import Command
from tests import tests_dir_path


def test_command_init_without_args():
    command = Command()
    assert command.command == []


def test_command_str():
    command = Command(["python", "run.py"])
    assert str(command) == "python run.py"


def test_command_validate_without_execution_call():
    command = Command()
    with pytest.raises(AttributeError):
        command.validate()


def test_command_validate_without_command_to_execute():
    command = Command().set_tool_command("python")
    with pytest.raises(AttributeError):
        command.validate()


def test_command_validate_without_command_to_execute_from_init():
    with pytest.raises(ValueError):
        Command(["python"])


def test_command_set_tool_execution_call_and_set_tool_command():
    command = Command()
    command.set_tool_execution_call("python").set_tool_command("run.py")
    assert command._execution_call == "python"
    assert command._command_to_execute == "run.py"


@pytest.mark.parametrize("args, expected_execution_call, expected_command_to_execute", [
    (["python", "run.py"], "python", "run.py"),
    (["java", "JarFile.jar"], "java", "JarFile.jar"),
    (["node", "index.js"], "node", "index.js"),
], ids=["python", "java", "node"])
def test_command_init_with_valid_args(args, expected_execution_call, expected_command_to_execute):
    command = Command(args)
    assert command._execution_call == expected_execution_call
    assert command._command_to_execute == expected_command_to_execute


@pytest.mark.parametrize("args", [
    (["python"]),
    (["java", None]),
    ([None, "run.py"]),
], ids=["single_arg", "none_value", "execution_call_none"])
def test_command_init_with_invalid_args(args):
    try:
        Command(args)
    except Exception as err:
        assert isinstance(err, (ValueError, TypeCheckError))


@pytest.mark.parametrize("option, value, expected_command", [
    ("--debug", None, ["python", "run.py", "--debug"]),
    ("--debug", "True", ["python", "run.py", "--debug", "True"]),
    ("--verbose", None, ["python", "run.py", "--verbose"]),
], ids=["option_only", "option_value", "another_option"])
def test_add_option(option, value, expected_command):
    command = Command(["python", "run.py"])
    command.add_option(option, value=value)
    assert command.command == expected_command


@pytest.mark.parametrize("options, expected_command", [
    (["--debug", "--verbose"], ["python", "run.py", "--debug", "--verbose"]),
    (["--debug", "--verbose", ("--option1", "value1"), ("--option2", "value2")],
     ["python", "run.py", "--debug", "--verbose", "--option1", "value1", "--option2", "value2"]),
], ids=["options_only", "options_kwargs"])
def test_add_options(options, expected_command):
    command = Command(["python", "run.py"])
    command.add_options(*options)
    assert command.command == expected_command


@pytest.mark.parametrize("args, expected_command", [
    (["arg1", "arg2"], ["python", "run.py", "arg1", "arg2"]),
    (["arg3", "arg4"], ["python", "run.py", "arg3", "arg4"]),
], ids=["two_args", "another_two_args"])
def test_add_command_arguments(args, expected_command):
    command = Command(["python", "run.py"])
    command.add_command_arguments(*args)
    assert command.command == expected_command


def test_add_command_path_arguments():
    expected_command = ["python", "run.py", os.path.relpath(tests_dir_path / r"tests_helpers/command/f1.txt"),
                        os.path.relpath( tests_dir_path / r"tests_helpers/command/")]
    paths = [tests_dir_path / r"tests_helpers/command/f1.txt", tests_dir_path / r"tests_helpers/command/"]
    command = Command(["python", "run.py"])
    command.add_command_path_arguments(*paths)
    assert command.command == expected_command


def test_add_invalid_command_path_arguments():
    with pytest.raises(FileNotFoundError):
        paths = ["test_helpers/command/f5"]
        command = Command(["python", "run.py"])
        command.add_command_path_arguments(*paths)


# Test updating delimiter
def test_set_values_delimiter():
    command = Command(["python", "run.py"])
    command.add_option("--option", "value1", delimiter="=")
    assert command.command == ["python", "run.py", "--option=value1"]
    command.set_values_delimiter(",", True)
    assert command.command == ["python", "run.py", "--option,value1"]


def test_set_values_delimiter_to_none():
    command = Command(["python", "run.py"]).add_option("--option", "value1", delimiter="=")
    assert command.command == ["python", "run.py", "--option=value1"]
    command.set_values_delimiter(None, True)
    assert command.command == ["python", "run.py", "--option", "value1"]


def test_set_values_delimiter_to_none_with_option_without_value_set():
    command_executors = ["python", "run.py"]
    opt1 = ("--option", "value1")
    opt2 = "--banana"
    command = ((Command(command_executors)
                .add_option(opt1[0], opt1[1], delimiter="="))
               .add_option(opt2))
    assert command.command == ["python", "run.py", "--option=value1", "--banana"]
    command.set_values_delimiter(None, True)
    assert (" ".join(command_executors) in str(command) and " ".join(opt1) in str(command)
            and "--banana" in command.command)


# Test updating delimiter when there was no delimiter before
def test_set_values_delimiter_with_no_delimiter_before():
    command = Command(["python", "run.py"])
    command.add_option("--option", "value1")
    assert command.command == ["python", "run.py", "--option", "value1"]
    command.set_values_delimiter(",", True)
    assert command.command == ["python", "run.py", "--option,value1"]


# Test updating delimiter with existing options
def test_update_values_delimiter_with_existing_options():
    command = Command(["python", "run.py"])
    command.add_option("--option1", "value1", delimiter="=")
    command.add_option("--option2", "value2", delimiter="=")
    assert command.command == ["python", "run.py", "--option1=value1", "--option2=value2"]
    command.set_values_delimiter(",", True)
    assert command.command == ["python", "run.py", "--option1,value1", "--option2,value2"]
    command.add_option("--option3", "value3")
    assert command.command == ["python", "run.py", "--option1,value1", "--option2,value2", "--option3,value3"]


# Test order of arguments and options
def test_order_of_arguments_and_options():
    command = Command(["python", "run.py"])
    command.add_command_arguments("arg1", "arg2")
    command.add_option("--option", "value")
    assert command.command == ["python", "run.py", "arg1", "arg2", "--option", "value"]
    command.add_command_arguments("arg3", "arg4")
    command.add_option("--option2", "value2")
    assert command.command == ["python", "run.py", "arg1", "arg2", "arg3", "arg4", "--option", "value", "--option2",
                               "value2"]


# Test order of arguments and options
def test_order_of_arguments_and_options_with_blank_arguments():
    command = Command(["python", "run.py"])
    command.add_command_arguments()
    command.add_option("--option", "value")
    assert command.command == ["python", "run.py", "--option", "value"]
    command.add_command_arguments("arg3", "arg4")
    command.add_option("--option2", "value2")
    assert command.command == ["python", "run.py", "arg3", "arg4", "--option", "value", "--option2",
                               "value2"]


# Test adding command path arguments
def test_add_command_path_arguments_with_absolute_paths():
    command = Command(["python", "run.py"])
    command.add_command_path_arguments(tests_dir_path / "tests_helpers/command/",
                                       tests_dir_path / "tests_helpers/command/f1.txt")
    assert command.command == ["python", "run.py", os.path.relpath(tests_dir_path / "tests_helpers/command/"),
                               os.path.relpath(tests_dir_path / "tests_helpers/command/f1.txt")]


# Test invalid delimiter
def test_invalid_values_delimiter():
    command = Command(["python", "run.py"])
    with pytest.raises(TypeCheckError):
        command.set_values_delimiter(123)


# Test multiple consecutive arguments
def test_add_consecutive_command_arguments():
    command = Command(["python", "run.py"])
    command.add_command_arguments("arg1", "arg2", "arg3")
    assert command.command == ["python", "run.py", "arg1", "arg2", "arg3"]


# Test adding options and then setting new delimiter
def test_add_options_and_set_new_delimiter():
    command = Command(["python", "run.py"])
    command.add_option("--option1", "value1")
    command.add_option("--option2", "value2")
    assert command.command == ["python", "run.py", "--option1", "value1", "--option2", "value2"]
    command.set_values_delimiter("=", True)
    command.add_option("--option3", "value3")
    assert command.command == ["python", "run.py", "--option1=value1", "--option2=value2", "--option3=value3"]


def test_add_options_and_set_new_delimiter_without_changing_previous():
    command = Command(["python", "run.py"])
    command.add_option("--option1", "value1")
    command.add_option("--option2", "value2")
    assert command.command == ["python", "run.py", "--option1", "value1", "--option2", "value2"]
    command.set_values_delimiter("=")
    command.add_option("--option3", "value3")
    assert command.command == ["python", "run.py", "--option1", "value1", "--option2", "value2", "--option3=value3"]
