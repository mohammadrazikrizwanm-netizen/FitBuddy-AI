from .config import (
    GEMINI_API_KEY,
    GEMINI_WORKOUT_MODEL,
    DEMO_MODE,
)


# ---------------------------------------------------------
# DEMO PLAN
# ---------------------------------------------------------

def _demo_plan(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str
):

    focus_map = {

        "weight loss":
            "full-body conditioning and moderate cardio",

        "muscle gain":
            "strength and progressive resistance",

        "general wellness":
            "balanced strength, cardio and mobility",

        "flexibility":
            "mobility, flexibility and light strength",
    }

    focus = focus_map.get(
        goal,
        "balanced fitness"
    )


    days = [

        (
            "Day 1",
            "Upper Body",
            "Warm-up 7 min; Push-ups 3 x 8-12; "
            "Rows 3 x 10; Shoulder press 3 x 10; "
            "Plank 3 x 30 sec",
            "5 min easy stretching"
        ),

        (
            "Day 2",
            "Lower Body",
            "Warm-up 7 min; Bodyweight squats 3 x 12; "
            "Reverse lunges 3 x 10 each side; "
            "Glute bridge 3 x 12; Calf raises 3 x 15",
            "5 min lower-body mobility"
        ),

        (
            "Day 3",
            "Cardio + Core",
            "Warm-up 5 min; Brisk walk/cycle 20-30 min; "
            "Dead bug 3 x 10 each side; "
            "Plank 3 x 30 sec",
            "Easy walk and breathing"
        ),

        (
            "Day 4",
            "Active Recovery",
            "Easy walk 20-30 min; Gentle mobility "
            "for hips, shoulders and back",
            "Keep effort comfortable"
        ),

        (
            "Day 5",
            "Full Body",
            "Warm-up 7 min; Squat 3 x 10; "
            "Incline push-up 3 x 10; "
            "Hip hinge 3 x 10; Row 3 x 10; "
            "Plank 3 x 30 sec",
            "5-8 min stretching"
        ),

        (
            "Day 6",
            "Goal Focus",
            f"20-30 min of {focus}; "
            "Keep technique controlled and rest "
            "60-90 seconds between sets",
            "Gentle cooldown"
        ),

        (
            "Day 7",
            "Recovery",
            "Rest or easy 20 min walk; "
            "Light mobility if comfortable",
            "Prioritize sleep and recovery"
        ),
    ]


    lines = [

        f"FITBUDDY 7-DAY FITNESS PLAN FOR {name.upper()}",

        (
            f"Profile: Age {age} | "
            f"Weight {weight:g} kg | "
            f"Goal: {goal} | "
            f"Intensity: {intensity}"
        ),

        "",

        (
            "Safety: This is general wellness guidance, "
            "not medical advice. Stop if you experience "
            "pain, dizziness or unusual symptoms."
        ),

        "",
    ]


    for (
        day,
        focus_name,
        workout,
        cooldown
    ) in days:

        lines.extend([

            f"{day} — {focus_name}",

            f"  • Workout: {workout}",

            f"  • Cooldown: {cooldown}",

            "",
        ])


    return "\n".join(lines)


# ---------------------------------------------------------
# GEMINI WORKOUT GENERATION
# ---------------------------------------------------------

def generate_workout_gemini(
    name,
    age,
    weight,
    goal,
    intensity
):

    # Demo mode
    if not GEMINI_API_KEY:

        if DEMO_MODE:

            return _demo_plan(
                name,
                age,
                weight,
                goal,
                intensity
            )

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )


    # Google GenAI SDK
    from google import genai


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a safe and practical personalized
7-day fitness plan.

USER INFORMATION:

Name: {name}

Age: {age}

Weight: {weight} kg

Goal: {goal}

Workout intensity: {intensity}


REQUIREMENTS:

Create exactly 7 days.

Each day should contain:

1. Day name
2. Workout focus
3. Warm-up
4. Exercises
5. Sets/repetitions or duration
6. Rest guidance
7. Cooldown/recovery

Use practical exercises that a beginner or
intermediate user can understand.

Do not prescribe medications.

Do not recommend dangerous challenges.

Do not recommend extreme dieting.

Do not make medical diagnoses.

If the user has pain, illness or medical
conditions, recommend consulting an appropriate
qualified professional.

Return the result as clean plain text.
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