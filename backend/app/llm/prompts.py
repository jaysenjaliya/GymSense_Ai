"""Prompt templates for workout analysis.

The template injects: current session JSON, summarized historical session data,
and the user profile. Keep templates here so they can be unit-tested.
"""

WORKOUT_ANALYSIS_TEMPLATE = """\
TODO: system + user prompt that asks the model to return workout analysis,
suggestions, progress analysis, consistency analysis, and future recommendations.

User profile:
{profile}

Current session:
{current_session}

Historical sessions (summarized):
{history}
"""


def build_workout_analysis_prompt(*, profile, current_session, history) -> str:
    # TODO: validate inputs and format the template
    return WORKOUT_ANALYSIS_TEMPLATE.format(
        profile=profile, current_session=current_session, history=history
    )
