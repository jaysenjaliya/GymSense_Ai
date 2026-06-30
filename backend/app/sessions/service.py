"""Session orchestration: drives the ML pipeline and persists results.

Pipeline (see app/ml): CSV validation -> preprocessing -> sliding windows ->
inference -> prediction smoothing -> segmentation -> rep counting -> analytics.
"""


async def process_upload(*args, **kwargs):
    """Run the full pipeline on an uploaded CSV and persist the session."""
    # TODO
    ...


async def list_sessions(*args, **kwargs):
    # TODO
    ...


async def get_session(*args, **kwargs):
    # TODO
    ...
