from dataclasses import dataclass
from typing import Optional


@dataclass
class HTMLFormOptions:
    isCustomForm: Optional[bool]


@dataclass
class HTMLFormMessageFieldBased(HTMLFormOptions):
    trueSuccess: str
    falseSuccess: str
    statusField: str


@dataclass
class HTMLFormDialog(HTMLFormOptions):
    dialogTitle: str
    dialogContent: str
