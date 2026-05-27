import logging
import os

import opik

from app.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


def configure_opik(settings: Settings) -> None:
    """Initialize Opik tracing. Disables @track when OPIK_API_KEY is not set."""
    if not settings.opik_api_key:
        opik.set_tracing_active(False)
        logger.info("OPIK_API_KEY not set — tracing disabled")
        return
    os.environ["OPIK_API_KEY"] = settings.opik_api_key
    if settings.opik_workspace:
        os.environ["OPIK_WORKSPACE"] = settings.opik_workspace
    os.environ["OPIK_PROJECT_NAME"] = settings.opik_project_name
    logger.info("Opik tracing enabled (project=%s)", settings.opik_project_name)
