from .config import (
    GEMINI_API_KEY,
    GEMINI_TIP_MODEL,
    DEMO_MODE,
)


def _demo_tip(goal: str):

    tips = {

        "weight loss":
            "Build meals around vegetables, a protein source "
            "and a sensible portion of carbohydrates. "
            "Stay hydrated and avoid extreme food restriction.",

        "muscle gain":
            "Include a protein-rich food in regular meals "
            "and enough overall food to support training "
            "and recovery.",

        "general wellness":
            "Aim for regular balanced meals, varied whole "
            "foods, adequate fluids and consistent sleep.",

        "flexibility":
            "Stay hydrated and include a variety of protein, "
            "fruits, vegetables and whole grains while "
            "prioritizing recovery and sleep.",
    }


    return tips.get(
        goal,
        tips["general wellness"]
    )


def generate_nutrition_tip_with_flash(
    goal: str
):

    # Demo mode
    if not GEMINI_API_KEY:

        if DEMO_MODE:

            return _demo_tip(goal)

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )


    from google import genai


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    prompt = f"""
Give one concise nutrition or recovery tip
for a fitness user whose goal is:

{goal}

Requirements:

- Practical
- General wellness guidance
- Safe
- Easy to understand
- Maximum 80 words
- Do not diagnose medical conditions
- Do not prescribe medication
- Do not prescribe supplements
- Do not encourage extreme dieting
"""


    response = client.models.generate_content(

        model=GEMINI_TIP_MODEL,

        contents=prompt,
    )


    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    return response.text.strip()