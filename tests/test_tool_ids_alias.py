"""Tests for tool_ids alias and Elastic namespace validation."""

from openskills.elastic_compat import validate_elastic_tool_namespaces
from openskills.models import Constraints, SkillContract


def _make_contract(tools: list[str] | None = None) -> SkillContract:
    constraints = Constraints(allowed_tools=tools) if tools is not None else None
    return SkillContract(
        openskills="1.0",
        name="test",
        description="Test.",
        constraints=constraints,
    )


class TestToolIdsAlias:
    def test_allowed_tools_field_works(self) -> None:
        c = Constraints(allowed_tools=["tool_a", "tool_b"])
        assert c.allowed_tools == ["tool_a", "tool_b"]

    def test_tool_ids_alias_populates_allowed_tools(self) -> None:
        data = {"tool_ids": ["platform.core.search", "security.alerts"]}
        c = Constraints.model_validate(data)
        assert c.allowed_tools == ["platform.core.search", "security.alerts"]

    def test_allowed_tools_by_name_still_works(self) -> None:
        data = {"allowed_tools": ["run_query"]}
        c = Constraints.model_validate(data)
        assert c.allowed_tools == ["run_query"]

    def test_contract_with_tool_ids_in_constraints(self) -> None:
        contract = SkillContract.model_validate({
            "openskills": "1.0",
            "name": "elastic-style",
            "description": "Uses tool_ids.",
            "constraints": {
                "tool_ids": [
                    "platform.core.execute_esql",
                    "platform.core.search",
                ],
            },
        })
        assert contract.allowed_tools == {
            "platform.core.execute_esql",
            "platform.core.search",
        }


class TestElasticNamespaceValidation:
    def test_valid_elastic_namespaces(self) -> None:
        contract = _make_contract([
            "platform.core.execute_esql",
            "security.alerts",
            "observability.investigation",
        ])
        assert validate_elastic_tool_namespaces(contract) == []

    def test_unknown_namespace_warns(self) -> None:
        contract = _make_contract(["custom.my_tool", "platform.core.search"])
        warnings = validate_elastic_tool_namespaces(contract)
        assert len(warnings) == 1
        assert "custom" in warnings[0]

    def test_non_dotted_names_ignored(self) -> None:
        contract = _make_contract(["run_query", "generate_report"])
        assert validate_elastic_tool_namespaces(contract) == []

    def test_no_tools(self) -> None:
        contract = _make_contract(None)
        assert validate_elastic_tool_namespaces(contract) == []

    def test_multiple_unknown_namespaces(self) -> None:
        contract = _make_contract(["foo.bar", "baz.qux"])
        warnings = validate_elastic_tool_namespaces(contract)
        assert len(warnings) == 2
