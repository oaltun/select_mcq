from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class ChoiceType(str, Enum):
    CHOICES = "choices"
    ONE_PAR_CHOICES = "oneparchoices"


class Choice(BaseModel):
    text: str
    is_correct: bool = False


class MultipleChoiceQuestion(BaseModel):
    question: str
    choices: List[Choice]
    choices_type: ChoiceType = ChoiceType.CHOICES
    solution: Optional[str] = None
