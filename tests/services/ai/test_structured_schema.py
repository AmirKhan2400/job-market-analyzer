from pydantic import BaseModel

from job_market_analyzer.domain.job import JobOffer
from job_market_analyzer.services.ai.structured_schema import strict_json_schema_for_model


class NestedDetails(BaseModel):
    label: str | None = None


class NestedModel(BaseModel):
    name: str | None = None
    details: NestedDetails | None = None


def test_strict_json_schema_requires_every_remaining_object_property():
    schema = strict_json_schema_for_model(
        JobOffer,
        exclude_properties={"description"},
    )

    assert "description" not in schema["properties"]
    assert set(schema["required"]) == set(schema["properties"])
    assert "company" in schema["required"]
    assert "role" in schema["required"]
    assert "preferred_skills" in schema["required"]
    assert schema["additionalProperties"] is False


def test_strict_json_schema_applies_to_nested_object_schemas():
    schema = strict_json_schema_for_model(NestedModel)

    details_schema = schema["$defs"]["NestedDetails"]

    assert set(schema["required"]) == {"name", "details"}
    assert schema["additionalProperties"] is False
    assert set(details_schema["required"]) == {"label"}
    assert details_schema["additionalProperties"] is False
