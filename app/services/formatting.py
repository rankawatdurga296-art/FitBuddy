from ..schemas import WorkoutPlan


def workout_plan_to_text(
    plan: WorkoutPlan
) -> str:

    lines = [
        plan.title,
        ""
    ]

    for day in plan.days:

        lines.extend(
            [
                day.day.upper(),
                f"Focus: {day.focus}",
                f"Warm-up: {day.warm_up}",
                "",
                "Exercises:",
            ]
        )

        for index, exercise in enumerate(
            day.exercises,
            start=1
        ):

            lines.append(
                f"{index}. {exercise.name} — "
                f"{exercise.sets}; "
                f"{exercise.reps_or_duration}; "
                f"Rest: {exercise.rest}"
            )

            if exercise.notes:

                lines.append(
                    f"   Note: {exercise.notes}"
                )

        lines.extend(
            [
                "",
                f"Cooldown: {day.cooldown}",
                f"Safety: {day.safety_note}",
                "",
            ]
        )

    if plan.general_notes:

        lines.append(
            "GENERAL NOTES"
        )

        lines.extend(
            f"• {note}"
            for note in plan.general_notes
        )

    return "\n".join(lines)