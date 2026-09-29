from functools import lru_cache

from ..config import settings
from ..schemas import (
    NutritionTip,
    UserInput,
    WorkoutPlan,
)


SYSTEM_SAFETY = """
You are the AI layer of FitBuddy, a general wellness
planning application.

Do not diagnose, prescribe, or claim to replace a doctor
or qualified trainer.

Avoid dangerous, extreme, punitive, or medically
prescriptive exercise or diet advice.

Never recommend starvation, dehydration, deliberate
overtraining, unsafe lifting, or exercising through
significant pain.

Prefer gradual, sustainable activity.

For users who may be minors, keep recommendations
age-appropriate and encourage adult/qualified professional
guidance for individualized or strenuous programs.

Use neutral, supportive language and do not make
body-shaming claims.
"""


@lru_cache(maxsize=1)
def get_client():

    from google import genai

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file before generating a plan."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )

def _generate_structured(
    model: str,
    prompt: str,
    schema: type
):
    client = get_client()

    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=6000,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    if getattr(response, "parsed", None) is not None:
        return response.parsed

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return schema.model_validate_json(
        response.text
    )

def generate_workout_gemini(
    user: UserInput
) -> WorkoutPlan:

    prompt = f"""
{SYSTEM_SAFETY}

Create a practical 7-day fitness plan for this profile:

- Name: {user.name}
- Age: {user.age}
- Weight: {user.weight_kg} kg
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

Requirements:

1. Return exactly 7 days.

2. Every day must include:
   - a focus
   - warm-up
   - at least one exercise
   - cooldown
   - safety note

3. Give sets/reps or duration and rest
   in plain language.

4. Include sensible recovery/rest days
   where appropriate.

5. Do not use bodyweight, weight, calorie,
   or appearance targets as a measure of worth.

6. Do not prescribe supplements or
   restrictive diets.

7. Make the plan adaptable.

8. A person should stop an exercise
   that causes pain.
"""

    return _generate_structured(
        settings.workout_model,
        prompt,
        WorkoutPlan
    )


def update_workout_plan(
    original_plan: str,
    user: UserInput,
    feedback: str
) -> WorkoutPlan:

    prompt = f"""
{SYSTEM_SAFETY}

Revise the existing FitBuddy 7-day plan
using the user's feedback.

User:

- Name: {user.name}
- Age: {user.age}
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

Feedback:

{feedback}

Existing plan:

{original_plan}

Requirements:

- Return exactly 7 days.

- Preserve useful parts of the existing
  plan unless feedback asks for a change.

- Apply the feedback safely and realistically.

- Keep the same structured fields.

- Include safety notes.

- Do not introduce extreme or dangerous
  exercise recommendations.
"""

    return _generate_structured(
        settings.workout_model,
        prompt,
        WorkoutPlan
    )


def generate_nutrition_tip_with_flash(
    user: UserInput
) -> NutritionTip:

    prompt = f"""
{SYSTEM_SAFETY}

Give one concise nutrition/recovery suggestion
for a user whose goal is "{user.goal}".

The user is {user.age} years old and prefers
{user.intensity} exercise.

Focus on ordinary balanced food, hydration,
sleep, or recovery habits.

Do not calculate calories.

Do not prescribe supplements.

Do not recommend restrictive eating.

Return a short practical tip plus a recovery note.
"""

    return _generate_structured(
        settings.nutrition_model,
        prompt,
        NutritionTip
    )