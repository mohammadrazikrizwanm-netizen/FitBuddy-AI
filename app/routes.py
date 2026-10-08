from pathlib import Path

from fastapi import (
    APIRouter,
    Request,
    Form,
)

from fastapi.responses import (
    HTMLResponse,
)

from fastapi.templating import (
    Jinja2Templates,
)


from .schemas import (
    UserInput,
    FeedbackRequest,
)


from .database import (
    save_user,
    get_user,
    save_plan,
    get_plan,
    update_plan,
    get_all_users,
    get_all_plans,
)


from .gemini_generator import (
    generate_workout_gemini,
)


from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)


from .updated_plan import (
    update_workout_plan,
)


from .config import ADMIN_KEY


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


def render_template(
    request: Request,
    name: str,
    context: dict,
    status_code: int = 200,
):
    """Render templates using Starlette's current request-first API."""
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=context,
        status_code=status_code,
    )


router = APIRouter()


# =========================================================
# HOME
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return render_template(
        request,
        "index.html",
        {
            "request": request
        }
    )


# =========================================================
# GENERATE WORKOUT
# =========================================================

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    user_id: str = Form(...),

    name: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),
):

    try:

        # Validate form data
        user = UserInput(

            user_id=user_id,

            name=name,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity,
        )


        # Generate workout
        workout_plan = generate_workout_gemini(

            user.name,

            user.age,

            user.weight,

            user.goal,

            user.intensity,
        )


        # Generate nutrition tip
        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user.goal
            )
        )


        # Save user
        save_user(
            user.model_dump()
        )


        # Save plan
        save_plan(

            user.user_id,

            workout_plan,

            nutrition_tip
        )


        # Display result
        return render_template(
            request,

            "result.html",

            {
                "request": request,

                "user": user,

                "workout_plan":
                    workout_plan,

                "nutrition_tip":
                    nutrition_tip,

                "updated":
                    False,

                "error":
                    None,
            }
        )


    except Exception as exc:

        return render_template(
            request,

            "index.html",

            {
                "request": request,

                "error":
                    f"Could not generate the plan: {exc}"
            },

            status_code=500
        )


# =========================================================
# SUBMIT FEEDBACK
# =========================================================

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),
):

    try:

        # Validate
        data = FeedbackRequest(

            user_id=user_id,

            feedback=feedback
        )


        # Get user
        user = get_user(
            data.user_id
        )


        # Get existing plan
        plan = get_plan(
            data.user_id
        )


        if not user or not plan:

            return render_template(
                request,

                "result.html",

                {
                    "request":
                        request,

                    "error":
                        "User ID not found. "
                        "Generate a plan first.",

                    "updated":
                        False
                },

                status_code=404
            )


        # Use updated plan if available,
        # otherwise original plan.
        current_plan = (
            plan.updated_plan
            or plan.original_plan
        )


        # Generate revised plan
        revised_plan = update_workout_plan(

            current_plan,

            data.feedback,

            user.goal,

            user.intensity
        )


        # Generate new nutrition tip
        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user.goal
            )
        )


        # Save update
        update_plan(

            data.user_id,

            revised_plan,

            data.feedback,

            nutrition_tip
        )


        return render_template(
            request,

            "result.html",

            {
                "request":
                    request,

                "user":
                    user,

                "workout_plan":
                    revised_plan,

                "nutrition_tip":
                    nutrition_tip,

                "updated":
                    True,

                "error":
                    None,
            }
        )


    except Exception as exc:

        return render_template(
            request,

            "result.html",

            {
                "request":
                    request,

                "error":
                    f"Could not update the plan: {exc}",

                "updated":
                    False
            },

            status_code=500
        )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(

    request: Request,

    key: str = ""
):

    # Simple project-level admin protection
    if key != ADMIN_KEY:

        return render_template(
            request,

            "admin_login.html",

            {
                "request":
                    request,

                "error":
                    None
            },

            status_code=401
        )


    users = get_all_users()

    plans_list = get_all_plans()


    plans = {
        plan.user_id: plan
        for plan in plans_list
    }


    return render_template(
        request,

        "all_users.html",

        {
            "request":
                request,

            "users":
                users,

            "plans":
                plans,
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "FitBuddy"
    }
