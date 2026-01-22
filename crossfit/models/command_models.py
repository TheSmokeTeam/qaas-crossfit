from enum import Enum
from typing import Union

from pydantic import BaseModel


class CommandType(Enum):
    SaveReport = "report"
    SnapshotCoverage = "snapshot"
    MergeCoverage = "merge"
    ResetCoverage = "reset"


class CommandResult(BaseModel):
    code: int
    command: str
    output: Union[str, None] = ""
    target: Union[str, None] = ""
    error: Union[str, None] = ""

    # exception: Union[str, None] = None

    def __add__(self, other):
        self.code &= other.code
        self.command += " && " + other.command
        self.output = "\n".join(filter(lambda val: val is not None, (self.output, other.output)))
        self.target = other.target or self.target
        self.error = "\n".join(filter(lambda val: val is not None, (self.error, other.error)))
        # self.exception = other.exception if other.exception is not None else self.exception
        return self

    def add_result(self, other):
        return self + other
