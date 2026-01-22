import os
from logging import Logger
from typing import Union

import crossfit.refs
from crossfit.tools import Jacoco, DotnetCoverage
from crossfit.models import ToolType


def create_tool(tool_type: ToolType, tool_path: str = None, cwd: Union[str, os.PathLike] = None, logger: Logger = None,
                catch: bool = True, **kwargs):
    if cwd: kwargs["cwd"] = cwd
    if tool_type == ToolType.Jacoco:
        return Jacoco(tool_path or crossfit.refs.tools_dir, logger, catch, **kwargs)
    elif tool_type == ToolType.DotnetCoverage:
        return DotnetCoverage(tool_path or crossfit.refs.tools_dir, logger, catch, **kwargs)
    else:
        raise ValueError(f"Unknown tool type: {tool_type}")
