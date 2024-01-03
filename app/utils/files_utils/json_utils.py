"""
A module for json utils in the app.utils.files utils package.
"""
import json
import logging
from typing import Any

import aiofiles

from app.config.init_settings import InitSettings
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)


def get_json_file_path(init_settings: InitSettings) -> str:
    """
    Get the file path for the Openapi.json file
    :param init_settings: Dependency method for cached init setting object
    :type init_settings: InitSettings
    :return: The path to the Openapi.json file
    :rtype: str
    """
    return f"{init_settings.OPENAPI_FILE_PATH}"


@with_logging
@benchmark
async def read_json_file(file_path: str, encoding: str) -> dict[str, Any]:
    """
    Read the OpenAPI JSON file
    :param file_path: Path of the file.
    :type file_path: str
    :param encoding: Encoding of the file.
    :type encoding: str
    :return: JSON data
    :rtype: dict[str, Any]
    """
    async with aiofiles.open(file_path, mode="r", encoding=encoding) as file:
        content = await file.read()
    if not content:
        raise ValueError(f"The file {file_path} is empty or not readable.")
    try:
        data: dict[str, Any] = json.loads(content)
        return data
    except json.JSONDecodeError as exc:
        raise ValueError(f"Error parsing JSON from {file_path}: {exc}") from exc


@with_logging
@benchmark
async def write_json_file(
    data: dict[str, Any],
    file_path: str,
    encoding: str,
) -> None:
    """
    Write the modified JSON data back to the file
    :param data: Modified JSON data
    :type data: dict[str, Any]
    :param file_path: Path of the file.
    :type file_path: str
    :param encoding: Encoding of the file.
    :type encoding: str
    :return: None
    :rtype: NoneType
    """
    async with aiofiles.open(
        file_path, mode="w", encoding=encoding
    ) as out_file:
        await out_file.write(json.dumps(data, indent=4, sort_keys=True))
