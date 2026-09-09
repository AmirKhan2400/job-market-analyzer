from copy import deepcopy
from typing import Any

from pydantic import BaseModel


def strict_json_schema_for_model(
    model: type[BaseModel],
    *,
    exclude_properties: set[str] | None = None,
) -> dict[str, Any]:
    schema = deepcopy(model.model_json_schema())

    for property_name in exclude_properties or set():
        schema.get("properties", {}).pop(property_name, None)

    _make_object_schemas_strict(schema)

    return schema


def _make_object_schemas_strict(schema: Any) -> None:
    if isinstance(schema, dict):
        if schema.get("type") == "object" or "properties" in schema:
            properties = schema.get("properties", {})
            if isinstance(properties, dict):
                schema["required"] = list(properties.keys())
                schema["additionalProperties"] = False

        for value in schema.values():
            _make_object_schemas_strict(value)
        return

    if isinstance(schema, list):
        for item in schema:
            _make_object_schemas_strict(item)
