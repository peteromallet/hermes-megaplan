"""
smart_model — PoC tool that automatically picks and switches to the best model
for a given task type.

The agent calls this with a task description, and the tool picks an appropriate
model (e.g., fast/cheap for simple tasks, powerful for complex ones) and switches.
"""

import json
import logging

from tools.registry import registry

logger = logging.getLogger(__name__)

# Simple task-to-model mapping — customize as needed
MODEL_PRESETS = {
    "fast": {
        "provider": "openrouter",
        "model": "google/gemini-2.5-flash",
        "description": "Fast and cheap — good for simple lookups, summaries, formatting",
    },
    "balanced": {
        "provider": "openrouter",
        "model": "anthropic/claude-sonnet-4",
        "description": "Good balance of speed and capability",
    },
    "powerful": {
        "provider": "openrouter",
        "model": "anthropic/claude-opus-4",
        "description": "Most capable — complex reasoning, coding, analysis",
    },
    "code": {
        "provider": "openrouter",
        "model": "anthropic/claude-sonnet-4",
        "description": "Optimized for code generation and debugging",
    },
}


def smart_model_handle(agent, preset: str, custom_provider: str = "", custom_model: str = "") -> str:
    """Pick a model based on preset or custom provider/model, then switch."""

    old_model = agent.model
    old_provider = agent.provider

    # Use custom if provided, otherwise look up preset
    if custom_provider and custom_model:
        provider = custom_provider
        model = custom_model
    elif preset in MODEL_PRESETS:
        provider = MODEL_PRESETS[preset]["provider"]
        model = MODEL_PRESETS[preset]["model"]
    else:
        return json.dumps({
            "success": False,
            "error": f"Unknown preset '{preset}'. Available: {list(MODEL_PRESETS.keys())}",
            "current": {"provider": old_provider, "model": old_model},
        })

    # Already on this model? No-op.
    if model == old_model and provider == old_provider:
        return json.dumps({
            "success": True,
            "message": f"Already using {model}",
            "current": {"provider": provider, "model": model},
        })

    # Delegate to agent's built-in switch
    result = agent._switch_model(provider, model)
    if result.get("success"):
        result["preset"] = preset if preset in MODEL_PRESETS else "custom"
    return json.dumps(result, ensure_ascii=False)


# ── Schema ──────────────────────────────────────────────────────────────

SMART_MODEL_SCHEMA = {
    "name": "smart_model",
    "description": (
        "Switch to a model preset suited for the current task. "
        "Presets: 'fast' (cheap/quick), 'balanced' (general), 'powerful' (complex reasoning), "
        "'code' (programming). Or provide custom provider+model."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "preset": {
                "type": "string",
                "enum": ["fast", "balanced", "powerful", "code", "custom"],
                "description": "Model preset to use, or 'custom' with provider+model.",
            },
            "provider": {
                "type": "string",
                "description": "Custom provider (only with preset='custom'). E.g. 'openrouter'.",
            },
            "model": {
                "type": "string",
                "description": "Custom model ID (only with preset='custom'). E.g. 'openai/gpt-4o'.",
            },
        },
        "required": ["preset"],
    },
}


def _check_smart_model() -> bool:
    return True


registry.register(
    name="smart_model",
    toolset="smart_model",
    schema=SMART_MODEL_SCHEMA,
    handler=lambda args, **kw: json.dumps({
        "error": "smart_model must be handled by the agent loop"
    }),
    check_fn=_check_smart_model,
)
