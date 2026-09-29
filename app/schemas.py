from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$"
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight_kg: float = Field(
        gt=20,
        le=300
    )

    goal: Goal

    intensity: Intensity

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return " ".join(value.split())


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$"
    )

    feedback: str = Field(
        min_length=5,
        max_length=1000
    )


class Exercise(BaseModel):

    name: str

    sets: str

    reps_or_duration: str

    rest: str

    notes: str = ""


class DayPlan(BaseModel):

    day: str

    focus: str

    warm_up: str

    exercises: list[Exercise] = Field(
        min_length=1
    )

    cooldown: str

    safety_note: str = ""


class WorkoutPlan(BaseModel):

    title: str

    days: list[DayPlan] = Field(
        min_length=7,
        max_length=7
    )

    general_notes: list[str] = Field(
        default_factory=list
    )


class NutritionTip(BaseModel):

    tip: str = Field(
        min_length=1,
        max_length=1000
    )

    recovery_note: str = Field(
        default="",
        max_length=1000
    )