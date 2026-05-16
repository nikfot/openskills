"""Elastic Agent Builder compatibility checks.

Validates that an OpenSkills contract conforms to Elastic naming
conventions and API limits.
"""

from __future__ import annotations

import re

from .models import SkillContract

ELASTIC_TOOL_NAMESPACES = frozenset({
    "platform",
    "security",
    "observability",
})

_ELASTIC_TOOL_RE = re.compile(r"^[a-z]+(?:\.[a-z_]+)+$")


def validate_elastic_tool_namespaces(contract: SkillContract) -> list[str]:
    """Warn if tool names don't follow Elastic's dotted namespace convention.

    Elastic built-in tools use ``platform.core.execute_esql``,
    ``security.alerts``, etc.  This check warns about tool names that
    look like they should be Elastic-namespaced but use the wrong prefix.

    Returns a list of warning strings (not errors -- custom tools may
    use arbitrary names).
    """
    warnings: list[str] = []
    if contract.allowed_tools is None:
        return warnings

    for tool in sorted(contract.allowed_tools):
        if "." in tool:
            prefix = tool.split(".")[0]
            if prefix not in ELASTIC_TOOL_NAMESPACES:
                warnings.append(
                    f"Tool '{tool}' uses dotted notation but prefix "
                    f"'{prefix}' is not a known Elastic namespace "
                    f"({', '.join(sorted(ELASTIC_TOOL_NAMESPACES))}). "
                    f"This may be a custom tool or a typo."
                )

    return warnings
