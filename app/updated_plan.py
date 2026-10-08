from .config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
    DEMO_MODE,
)


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
):

    # -----------------------------------------------------
    # DEMO MODE
    # -----------------------------------------------------

    if not GEMINI_API_KEY:

        if DEMO_MODE:

            return (
                original_plan
                + "\n\n"
                + "--- FITBUDDY FEEDBACK UPDATE ---\n"
                + f"Requested change: {feedback}\n\n"
                + (
                    "The requested change has been considered "
                    "while keeping the original weekly structure "
                    "and maintaining a conservative training load."
                )
            )

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )


    # -----------------------------------------------------
    # GEMINI
    # -----------------------------------------------------

    from google import genai


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    prompt = f"""
You are FitBuddy.

Revise the following existing 7-day fitness plan
according to the user's feedback.

FITNESS GOAL:

{goal}

INTENSITY:

{intensity}


USER FEEDBACK:

{feedback}


ORIGINAL PLAN:

{original_plan}


TASK:

Return the complete revised 7-day plan.

Do not return only the changed day.

Apply the user's feedback where reasonable.

Keep useful parts of the original plan.

Maintain safe and practical exercise recommendations.

Do not recommend dangerous exercise.

Do not prescribe medication.

Do not prescribe extreme diets.

Return clean plain text.
"""


    response = client.models.generate_content(

        model=GEMINI_WORKOUT_MODEL,

        contents=prompt,
    )


    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    return response.text.strip()