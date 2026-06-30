"""LLM integration (Anthropic): build prompt, call model, parse structured reply.

Kept isolated from FastAPI request/response concerns so prompts and parsing are
independently testable.
"""


async def analyze_workout(*args, **kwargs):
    """Render the prompt, call the LLM, and parse its response into a schema."""
    # TODO: assemble prompt (app.llm.prompts), call Anthropic client, parse output
    ...
