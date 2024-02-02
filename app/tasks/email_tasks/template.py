"""
A module for template in the app.utils package.
"""

import logging
from pathlib import Path
from typing import Annotated, Any

import aiofiles
from fastapi import Depends
from jinja2 import Template

from app.config.config import get_init_settings
from app.config.init_settings import InitSettings
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)


def render_template(template: str, environment: dict[str, Any]) -> str:
    """
    Renders the given template with the given environment variables
    :param template: The body of the email in HTML format
    :type template: str
    :param environment: A dictionary of variables used in the email
     templates
    :type environment: dict[str, Any]
    :return: Rendered template with environment variables
    :rtype: str
    """
    return Template(template).render(environment)


@with_logging
@benchmark
async def read_template_file(
        template_path: str | Path,
    init_settings: Annotated[InitSettings, Depends(get_init_settings)],
) -> str:
    """
    Read the template file
    :param template_path: Path to the template
    :type template_path: Union[str, Path]
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :return: Template string
    :rtype: str
    """
    async with aiofiles.open(
        template_path, mode="r", encoding=init_settings.ENCODING
    ) as file:
        return await file.read()
