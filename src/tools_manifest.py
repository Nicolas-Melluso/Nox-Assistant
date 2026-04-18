"""Fachada del manifiesto de tools basada en src.skills.registry."""

from src.skills.registry import get_tool_names, get_tools_manifest

TOOLS: list[dict] = get_tools_manifest()
TOOL_NAMES: set[str] = get_tool_names()
