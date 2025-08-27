"""
Data models for the Paper to Voice Assistant
"""

import operator
from typing import Annotated, TypedDict
from langchain_core.pydantic_v1 import BaseModel


class State(TypedDict):
    image_path: str
    steps: Annotated[list, operator.add]
    substeps: Annotated[list, operator.add]
    solutions: Annotated[list, operator.add]
    
    content: str
    plan: str
    Dialog: Annotated[list, operator.add]


class Task(BaseModel):
    task: str


class SubStep(BaseModel):
    substep: str


class StepState(TypedDict):
    step: str
    image_path: str
    solutions: str
    Dialog: str
