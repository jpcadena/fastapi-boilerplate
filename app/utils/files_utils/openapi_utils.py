"""
A module for openapi utils in the app.utils.files utils package.
"""

import json
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute


def remove_tag_from_operation_id(tag: str, operation_id: str) -> str:
    """
    Remove tag from the operation ID
    :param tag: Tag to remove
    :type tag: str
    :param operation_id: Original operation ID
    :type operation_id: str
    :return: Updated operation ID
    :rtype: str
    """
    return operation_id.removeprefix(f"{tag}-")


def update_operation_id(operation: dict[str, Any]) -> None:
    """
    Update the operation ID of a single operation.
    :param operation: Operation object
    :type operation: dict[str, Any]
    :return: None
    :rtype: NoneType
    """
    if operation.get(
        "tags",
    ):
        tag: str = operation["tags"][0]
        operation_id: str = operation["operationId"]
        new_operation_id: str = remove_tag_from_operation_id(tag, operation_id)
        operation["operationId"] = new_operation_id


def modify_json_data(
    data: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Modify the JSON data
    :param data: JSON data to modify
    :type data: dict[str, Any]
    :return: Modified JSON data
    :rtype: dict[str, Any]
    """
    paths: dict[str, dict[str, dict[str, Any]]] | None = data.get("paths")
    if not paths:
        return data
    for key, path_data in paths.items():
        if key == "/":
            continue
        for operation in dict(path_data).values():
            update_operation_id(operation)
    return data


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a custom unique ID for each route in API
    :param route: endpoint route
    :type route: APIRoute
    :return: new ID based on tag and route name
    :rtype: str
    """
    if route.name in (
        "redirect_to_docs",
        "check_health",
    ):
        return str(route.name)
    return f"{route.tags[0]}-{route.name}"


def write_schema_to_file(
    schema: dict[str, dict[str, Any]], file_path: str, encoding: str
) -> None:
    """
    Writes the given schema to a file.
    :param schema: Schema to write.
    :type schema: dict[str, dict[str, Any]]
    :param file_path: Path of the file.
    :type file_path: str
    :param encoding: Encoding of the file.
    :type encoding: str
    :return: None
    :rtype: NoneType
    """
    with open(file_path, mode="w", encoding=encoding) as out_file:
        out_file.write(json.dumps(schema, indent=4))


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    """
    Generate a custom OpenAPI schema for the application.
    This function customizes the default FastAPI OpenAPI generation by
    incorporating additional configuration settings and modifying the schema.
    The modified schema is then cached for subsequent requests.
    :param app: FastAPI instance.
    :type app: FastAPI
    :return: Customized OpenAPI schema.
    :rtype: dict[str, Any]
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema: dict[str, dict[str, Any]] = get_openapi(
        title=app.state.init_settings.PROJECT_NAME,
        version=app.state.init_settings.VERSION,
        summary=app.state.init_settings.SUMMARY,
        description=app.state.init_settings.DESCRIPTION,
        routes=app.routes,
        servers=[
            {
                "url": app.state.auth_settings.SERVER_URL,
                "description": app.state.auth_settings.SERVER_DESCRIPTION,
            }
        ],
        contact=app.state.settings.CONTACT,
        license_info=app.state.init_settings.LICENSE_INFO,
    )
    openapi_schema = modify_json_data(openapi_schema)
    app.openapi_schema = openapi_schema
    write_schema_to_file(
        openapi_schema,
        f"{app.state.init_settings.OPENAPI_FILE_PATH}"[1:],
        app.state.init_settings.ENCODING,
    )
    return app.openapi_schema
