from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import User, WorkoutPlan, get_db
from .dependencies import require_admin, security
from .schemas import FeedbackRequest, UserInput
from .services.formatting import workout_plan_to_text
from .services.gemini import (
    generate_nutrition_tip_with_flash,
    generate_workout_gemini,
    update_workout_plan,
)

router = APIRouter()

TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _error_context(request: Request, message: str):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"message": message},
        status_code=400,
    )


# =========================
# HOME
# =========================

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


# =========================
# GENERATE WORKOUT
# =========================

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight_kg: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user_input = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight_kg=weight_kg,
            goal=goal,
            intensity=intensity,
        )
    except Exception as exc:
       return _error_context(request, f"Invalid input: {exc}")


    try:
        workout = generate_workout_gemini(user_input)
        nutrition = generate_nutrition_tip_with_flash(user_input)
    except Exception as exc:
      import traceback
      traceback.print_exc()
      return _error_context(request, str(exc))

    existing = db.scalar(
        select(User).where(User.user_id == user_input.user_id)
    )

    if existing:
        existing.name = user_input.name
        existing.age = user_input.age
        existing.weight_kg = user_input.weight_kg
        existing.goal = user_input.goal
        existing.intensity = user_input.intensity

        user = existing
        plan = user.plan

        if plan:
            plan.original_plan = workout_plan_to_text(workout)
            plan.updated_plan = None
            plan.feedback = None
            plan.nutrition_tip = (
                f"{nutrition.tip}\n\n"
                f"Recovery: {nutrition.recovery_note}"
            )
            plan.updated_at = None
        else:
            plan = WorkoutPlan(
                user=user,
                original_plan=workout_plan_to_text(workout),
                nutrition_tip=(
                    f"{nutrition.tip}\n\n"
                    f"Recovery: {nutrition.recovery_note}"
                ),
            )
            db.add(plan)

    else:
        user = User(
            user_id=user_input.user_id,
            name=user_input.name,
            age=user_input.age,
            weight_kg=user_input.weight_kg,
            goal=user_input.goal,
            intensity=user_input.intensity,
        )

        plan = WorkoutPlan(
            user=user,
            original_plan=workout_plan_to_text(workout),
            nutrition_tip=(
                f"{nutrition.tip}\n\n"
                f"Recovery: {nutrition.recovery_note}"
            ),
        )

        db.add(user)
        db.add(plan)

    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "current_plan": plan.updated_plan or plan.original_plan,
            "message": None,
        },
    )


# =========================
# SUBMIT FEEDBACK
# =========================

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        feedback_request = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )
    except Exception as exc:
        return _error_context(request, f"Invalid feedback: {exc}")

    user = db.scalar(
        select(User).where(User.user_id == feedback_request.user_id)
    )

    if not user or not user.plan:
        return _error_context(
            request,
            "No saved plan was found for that User ID.",
        )

    try:
        profile = UserInput(
            user_id=user.user_id,
            name=user.name,
            age=user.age,
            weight_kg=user.weight_kg,
            goal=user.goal,
            intensity=user.intensity,
        )

        revised = update_workout_plan(
            user.plan.original_plan,
            profile,
            feedback_request.feedback,
        )

        nutrition = generate_nutrition_tip_with_flash(profile)

    except Exception as exc:
        return _error_context(request, str(exc))

    user.plan.updated_plan = workout_plan_to_text(revised)
    user.plan.feedback = feedback_request.feedback
    user.plan.nutrition_tip = (
        f"{nutrition.tip}\n\n"
        f"Recovery: {nutrition.recovery_note}"
    )
    user.plan.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": user.plan,
            "current_plan": user.plan.updated_plan,
            "message": "Your plan was updated using the feedback.",
        },
    )


# =========================
# ADMIN - VIEW USERS
# =========================

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    require_admin(credentials)

    users = db.scalars(
        select(User).order_by(User.created_at.desc())
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )


# =========================
# ADMIN - DELETE USER
# =========================

@router.post("/admin/delete/{user_id}")
def delete_user(
    user_id: int,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    require_admin(credentials)

    user = db.get(User, user_id)

    if user:
        db.delete(user)
        db.commit()

    return RedirectResponse(
        "/view-all-users",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# =========================
# API - GENERATE WORKOUT
# =========================

@router.post("/api/generate-workout")
def api_generate_workout(
    payload: UserInput,
    db: Session = Depends(get_db),
):
    workout = generate_workout_gemini(payload)
    nutrition = generate_nutrition_tip_with_flash(payload)

    existing = db.scalar(
        select(User).where(User.user_id == payload.user_id)
    )

    if existing:
        user = existing

        user.name = payload.name
        user.age = payload.age
        user.weight_kg = payload.weight_kg
        user.goal = payload.goal
        user.intensity = payload.intensity

        plan = user.plan

        if plan:
            plan.original_plan = workout_plan_to_text(workout)
            plan.updated_plan = None
            plan.feedback = None
            plan.nutrition_tip = (
                f"{nutrition.tip}\n\n"
                f"Recovery: {nutrition.recovery_note}"
            )
            plan.updated_at = None

        else:
            plan = WorkoutPlan(
                user=user,
                original_plan=workout_plan_to_text(workout),
                nutrition_tip=(
                    f"{nutrition.tip}\n\n"
                    f"Recovery: {nutrition.recovery_note}"
                ),
            )
            db.add(plan)

    else:
        user = User(
            user_id=payload.user_id,
            name=payload.name,
            age=payload.age,
            weight_kg=payload.weight_kg,
            goal=payload.goal,
            intensity=payload.intensity,
        )

        plan = WorkoutPlan(
            user=user,
            original_plan=workout_plan_to_text(workout),
            nutrition_tip=(
                f"{nutrition.tip}\n\n"
                f"Recovery: {nutrition.recovery_note}"
            ),
        )

        db.add(user)
        db.add(plan)

    db.commit()
    db.refresh(user)

    return {
        "user": {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight_kg": user.weight_kg,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "workout_plan": plan.original_plan,
        "nutrition_tip": plan.nutrition_tip,
    }


# =========================
# API - SUBMIT FEEDBACK
# =========================

@router.post("/api/submit-feedback")
def api_submit_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.user_id == payload.user_id)
    )

    if not user or not user.plan:
        raise HTTPException(
            status_code=404,
            detail="No saved plan was found for that User ID.",
        )

    profile = UserInput(
        user_id=user.user_id,
        name=user.name,
        age=user.age,
        weight_kg=user.weight_kg,
        goal=user.goal,
        intensity=user.intensity,
    )

    revised = update_workout_plan(
        user.plan.original_plan,
        profile,
        payload.feedback,
    )

    nutrition = generate_nutrition_tip_with_flash(profile)

    user.plan.updated_plan = workout_plan_to_text(revised)
    user.plan.feedback = payload.feedback
    user.plan.nutrition_tip = (
        f"{nutrition.tip}\n\n"
        f"Recovery: {nutrition.recovery_note}"
    )
    user.plan.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return {
        "user_id": user.user_id,
        "updated_plan": user.plan.updated_plan,
        "nutrition_tip": user.plan.nutrition_tip,
        "feedback": user.plan.feedback,
    }


# =========================
# API - GET USER
# =========================

@router.get("/api/users/{user_id}")
def api_get_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.user_id == user_id)
    )

    if not user or not user.plan:
        raise HTTPException(
            status_code=404,
            detail="User or plan not found.",
        )

    return {
        "user_id": user.user_id,
        "name": user.name,
        "age": user.age,
        "weight_kg": user.weight_kg,
        "goal": user.goal,
        "intensity": user.intensity,
        "original_plan": user.plan.original_plan,
        "updated_plan": user.plan.updated_plan,
        "feedback": user.plan.feedback,
        "nutrition_tip": user.plan.nutrition_tip,
    }


# =========================
# HEALTH CHECK
# =========================

@router.get("/health")
def health():
    return {"status": "ok"}