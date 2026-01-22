from enum import Enum


class ToolType(Enum):
    Jacoco: str = "jacococli.jar"
    DotnetCoverage: str = "dotnet-coverage"
    DotnetReportGenerator: str = "reportgenerator"


class ReportFormat(Enum):
    Csv = "Csv"
    Html = "Html"
    Xml = "Xml"
    Cobertura = "Cobertura"
