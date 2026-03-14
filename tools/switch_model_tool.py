"""
switch_model tool — lets the agent discover available models/providers
and switch to a different one mid-conversation.

Two actions:
  - list: show current model, original model, and available providers+models
  - switch: change to a different provider/model at runtime
"""

import json
import logging

from tools.registry import registry

logger = logging.getLogger(__name__)


def switch_model_list(
    current_provider: str,
    current_model: str,
    original: dict,
) -> str:
    """Return JSON describing current state and available providers/models."""
    from hermes_cli.models import list_available_providers, curated_models_for_provider

    available = []
    for prov in list_available_providers():
        models = curated_models_for_provider(prov["id"])
        available.append({
            "provider": prov["id"],
            "label": prov["label"],
            "authenticated": prov["authenticated"],
            "models": [m_id for m_id, _ in models],
        })

    return json.dumps({
        "current": {"provider": current_provider, "model": current_model},
        "original": original,
        "available_providers": available,
    }, ensure_ascii=False)


def switch_model_switch(
    provider: str,
    model: str,
    reason: str,
    agent,  # AIAgent — imported at call site to avoid circular import
) -> str:
    """Ask the agent to switch its model/provider in-place.

    Delegates to agent._switch_model() which handles client construction.
    Returns JSON the agent sees as its tool result.
    """
    if not provider or not model:
        return json.dumps({
            "success": False,
            "error": "Both 'provider' and 'model' are required for switch action.",
            "current": {"provider": agent.provider, "model": agent.model},
        }, ensure_ascii=False)

    if reason:
        logger.info("switch_model reason: %s", reason)

    result = agent._switch_model(provider, model)
    return json.dumps(result, ensure_ascii=False)


# ── Schema ──────────────────────────────────────────────────────────────

SWITCH_MODEL_SCHEMA = {
    "name": "switch_model",
    "description": (
        "Discover available LLM providers/models and switch to a different one "
        "mid-conversation. Use action='list' to see what's available, then "
        "action='switch' to change. Consider switching to a faster/cheaper model "
        "for simple tasks, or a more capable model for complex reasoning."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "switch"],
                "description": "Action to perform: 'list' shows available models, 'switch' changes the active model.",
            },
            "provider": {
                "type": "string",
                "description": "Provider to switch to (required for 'switch'). E.g. 'openrouter', 'nous', 'anthropic'.",
            },
            "model": {
                "type": "string",
                "description": "Model ID to switch to (required for 'switch'). E.g. 'anthropic/claude-sonnet-4-6'.",
            },
            "reason": {
                "type": "string",
                "description": "Optional: why you're switching (logged for observability).",
            },
        },
        "required": ["action"],
    },
}


def _check_switch_model() -> bool:
    """Always available when loaded."""
    return True


# ── Registration ────────────────────────────────────────────────────────

registry.register(
    name="switch_model",
    toolset="switch_model",
    schema=SWITCH_MODEL_SCHEMA,
    # Handler is a stub — actual dispatch happens in run_agent._invoke_tool()
    # because this tool needs agent-level state access.
    handler=lambda args, **kw: json.dumps({
        "error": "switch_model must be handled by the agent loop"
    }),
    check_fn=_check_switch_model,
)
