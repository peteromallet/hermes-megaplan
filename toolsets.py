#!/usr/bin/env python3
"""Toolset definitions for Hermes Agent.
"""
from typing import List, Dict, Any, Set, Optional


# Shared tool list for CLI and all messaging platform toolsets.
# Edit this once to update all platforms simultaneously.
_HERMES_CORE_TOOLS = [
    # Web
    "web_search", "web_extract",
    # Terminal + process management
    "terminal", "process",
    # File manipulation
    "read_file", "write_file", "patch", "search_files",
    # Vision + image generation
    "vision_analyze", "image_generate",
    # MoA
    "mixture_of_agents",
    # Skills
    "skills_list", "skill_view", "skill_manage",
    # Browser automation
    "browser_navigate", "browser_snapshot", "browser_click",
    "browser_type", "browser_scroll", "browser_back",
    "browser_press", "browser_close", "browser_get_images",
    "browser_vision",
    # Text-to-speech
    "text_to_speech",
    # Planning & memory
    "todo", "memory",
    # Self-command (agent executes its own slash commands via control API)
    "run_command",
    # Session history search
    "session_search",
    # Clarifying questions
    "clarify",
    # Code execution + delegation
    "execute_code", "delegate_task",
    # Cronjob management
    "schedule_cronjob", "list_cronjobs", "remove_cronjob",
    # Cross-platform messaging (gated on gateway running via check_fn)
    "send_message",
    # Honcho memory tools (gated on honcho being active via check_fn)
    "honcho_context", "honcho_profile", "honcho_search", "honcho_conclude",
    # Home Assistant smart home control (gated on HASS_TOKEN via check_fn)
    "ha_list_entities", "ha_get_state", "ha_list_services", "ha_call_service",
]


# Core toolset definitions
# These can include individual tools or reference other toolsets
TOOLSETS = {
    # Basic toolsets - individual tool categories
    "web": {
        "description": "Web research and content extraction tools",
        "tools": ["web_search", "web_extract"],
        "includes": []  # No other toolsets included
    },
    
    "search": {
        "description": "Web search only (no content extraction/scraping)",
        "tools": ["web_search"],
        "includes": []
    },
    
    "vision": {
        "description": "Image analysis and vision tools",
        "tools": ["vision_analyze"],
        "includes": []
    },
    
    "image_gen": {
        "description": "Creative generation tools (images)",
        "tools": ["image_generate"],
        "includes": []
    },
    
    "terminal": {
        "description": "Terminal/command execution and process management tools",
        "tools": ["terminal", "process"],
        "includes": []
    },

    "run_command": {
        "description": "Execute slash commands via the local control API (self-command)",
        "tools": ["run_command"],
        "includes": []
    },
    
    "moa": {
        "description": "Advanced reasoning and problem-solving tools",
        "tools": ["mixture_of_agents"],
        "includes": []
    },
    
    "skills": {
        "description": "Access, create, edit, and manage skill documents with specialized instructions and knowledge",
        "tools": ["skills_list", "skill_view", "skill_manage"],
        "includes": []
    },
    
    "browser": {
        "description": "Browser automation for web interaction (navigate, click, type, scroll, iframes, hold-click) with web search for finding URLs",
        "tools": [
            "browser_navigate", "browser_snapshot", "browser_click",
            "browser_type", "browser_scroll", "browser_back",
            "browser_press", "browser_close", "browser_get_images",
            "browser_vision", "web_search"
        ],
        "includes": []
    },
    
    "cronjob": {
        "description": "Cronjob management tools - schedule, list, and remove automated tasks",
        "tools": ["schedule_cronjob", "list_cronjobs", "remove_cronjob"],
        "includes": []
    },
    
    "rl": {
        "description": "RL training tools for running reinforcement learning on Tinker-Atropos",
        "tools": [
            "rl_list_environments", "rl_select_environment",
            "rl_get_current_config", "rl_edit_config",
            "rl_start_training", "rl_check_status",
            "rl_stop_training", "rl_get_results",
            "rl_list_runs", "rl_test_inference"
        ],
        "includes": []
    },
    
    "file": {
        "description": "File manipulation tools: read, write, patch (with fuzzy matching), and search (content + files)",
        "tools": ["read_file", "write_file", "patch", "search_files"],
        "includes": []
    },
    
    "tts": {
        "description": "Text-to-speech: convert text to audio with Edge TTS (free), ElevenLabs, or OpenAI",
        "tools": ["text_to_speech"],
        "includes": []
    },
    
    "todo": {
        "description": "Task planning and tracking for multi-step work",
        "tools": ["todo"],
        "includes": []
    },
    
    "memory": {
        "description": "Persistent memory across sessions (personal notes + user profile)",
        "tools": ["memory"],
        "includes": []
    },
    
    "session_search": {
        "description": "Search and recall past conversations with summarization",
        "tools": ["session_search"],
        "includes": []
    },
    
    "clarify": {
        "description": "Ask the user clarifying questions (multiple-choice or open-ended)",
        "tools": ["clarify"],
        "includes": []
    },
    
    "code_execution": {
        "description": "Run Python scripts that call tools programmatically (reduces LLM round trips)",
        "tools": ["execute_code"],
        "includes": []
    },
    
    "delegation": {
        "description": "Spawn subagents with isolated context for complex subtasks",
        "tools": ["delegate_task"],
        "includes": []
    },

    "honcho": {
        "description": "Honcho AI-native memory for persistent cross-session user modeling",
        "tools": ["honcho_context", "honcho_profile", "honcho_search", "honcho_conclude"],
        "includes": []
    },

    "homeassistant": {
        "description": "Home Assistant smart home control and monitoring",
        "tools": ["ha_list_entities", "ha_get_state", "ha_list_services", "ha_call_service"],
        "includes": []
    },


    # Scenario-specific toolsets
    
    "debugging": {
        "description": "Debugging and troubleshooting toolkit",
        "tools": ["terminal", "process"],
        "includes": ["web", "file"]  # For searching error messages and solutions, and file operations
    },
    
    "safe": {
        "description": "Safe toolkit without terminal access",
        "tools": ["mixture_of_agents"],
        "includes": ["web", "vision", "image_gen"]
    },

    "hermes-cli": {
        "description": "Full interactive CLI toolset - all default tools plus cronjob management",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },
    
    "hermes-telegram": {
        "description": "Telegram bot toolset - full access for personal use (terminal has safety checks)",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },
    
    "hermes-discord": {
        "description": "Discord bot toolset - full access (terminal has safety checks via dangerous command approval)",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },
    
    "hermes-whatsapp": {
        "description": "WhatsApp bot toolset - similar to Telegram (personal messaging, more trusted)",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },
    
    "hermes-slack": {
        "description": "Slack bot toolset - full access for workspace use (terminal has safety checks)",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },
    
    "hermes-signal": {
        "description": "Signal bot toolset - encrypted messaging platform (full access)",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },

    "hermes-homeassistant": {
        "description": "Home Assistant bot toolset - smart home event monitoring and control",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },

    "hermes-email": {
        "description": "Email bot toolset - interact with Hermes via email (IMAP/SMTP)",
        "tools": _HERMES_CORE_TOOLS,
        "includes": []
    },

    "hermes-gateway": {
        "description": "Gateway toolset - union of all messaging platform tools",
        "tools": [],
        "includes": ["hermes-telegram", "hermes-discord", "hermes-whatsapp", "hermes-slack", "hermes-signal", "hermes-homeassistant", "hermes-email"]
    }
}



def get_toolset(name: str) -> Optional[Dict[str, Any]]:
    """Return toolset definition by name, or None if not found."""
    return TOOLSETS.get(name)


def resolve_toolset(name: str, visited: Set[str] = None) -> List[str]:
    """Recursively resolve toolset (and its includes) to list of tool names. Handles 'all'/* aliases and cycle detection."""
    if visited is None:
        visited = set()
    
    if name in {"all", "*"}:
        all_tools: Set[str] = set()
        for toolset_name in get_toolset_names():
            resolved = resolve_toolset(toolset_name, visited.copy())
            all_tools.update(resolved)
        return list(all_tools)

    if name in visited:
        print(f"⚠️  Circular dependency detected in toolset '{name}'")
        return []
    
    visited.add(name)
    
    toolset = TOOLSETS.get(name)
    if not toolset:
        return []
    
    tools = set(toolset.get("tools", []))
    
    for included_name in toolset.get("includes", []):
        included_tools = resolve_toolset(included_name, visited.copy())
        tools.update(included_tools)
    
    return list(tools)


def resolve_multiple_toolsets(toolset_names: List[str]) -> List[str]:
    """Resolve multiple toolsets and return deduplicated combined tool list."""
    all_tools = set()
    for name in toolset_names:
        tools = resolve_toolset(name)
        all_tools.update(tools)
    return list(all_tools)


def get_all_toolsets() -> Dict[str, Dict[str, Any]]:
    """Return copy of all toolset definitions."""
    return TOOLSETS.copy()


def get_toolset_names() -> List[str]:
    """Return list of all toolset names."""
    return list(TOOLSETS.keys())




def validate_toolset(name: str) -> bool:
    """Return True if toolset name is valid (including special 'all'/* aliases)."""
    if name in {"all", "*"}:
        return True
    return name in TOOLSETS


def create_custom_toolset(
    name: str,
    description: str,
    tools: List[str] = None,
    includes: List[str] = None
) -> None:
    """Add or update a custom toolset definition at runtime."""
    TOOLSETS[name] = {
        "description": description,
        "tools": tools or [],
        "includes": includes or []
    }




def get_toolset_info(name: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a toolset including resolved tools."""
    toolset = get_toolset(name)
    if not toolset:
        return None

    resolved_tools = resolve_toolset(name)

    return {
        "name": name,
        "description": toolset["description"],
        "direct_tools": toolset["tools"],
        "includes": toolset["includes"],
        "resolved_tools": resolved_tools,
        "tool_count": len(resolved_tools),
        "is_composite": len(toolset["includes"]) > 0
    }


def print_toolset_tree(name: str, indent: int = 0) -> None:
    """
    Print a tree view of a toolset and its composition.
    
    Args:
        name (str): Toolset name
        indent (int): Current indentation level
    """
    prefix = "  " * indent
    toolset = get_toolset(name)
    
    if not toolset:
        print(f"{prefix}❌ Unknown toolset: {name}")
        return
    
    print(f"{prefix}📦 {name}: {toolset['description']}")
    
    if toolset["tools"]:
        print(f"{prefix}  🔧 Tools: {', '.join(toolset['tools'])}")
    
    if toolset["includes"]:
        print(f"{prefix}  📂 Includes:")
        for included in toolset["includes"]:
            print_toolset_tree(included, indent + 2)


if __name__ == "__main__":
    print("Toolsets System Demo")
    print("=" * 60)
    
    print("\nAvailable Toolsets:")
    print("-" * 40)
    for name, toolset in get_all_toolsets().items():
        info = get_toolset_info(name)
        composite = "[composite]" if info["is_composite"] else "[leaf]"
        print(f"  {composite} {name:20} - {toolset['description']}")
        print(f"     Tools: {len(info['resolved_tools'])} total")
    
    print("\nToolset Resolution Examples:")
    print("-" * 40)
    for name in ["web", "terminal", "safe", "debugging"]:
        tools = resolve_toolset(name)
        print(f"\n  {name}:")
        print(f"    Resolved to {len(tools)} tools: {', '.join(sorted(tools))}")
    
    print("\nMultiple Toolset Resolution:")
    print("-" * 40)
    combined = resolve_multiple_toolsets(["web", "vision", "terminal"])
    print("  Combining ['web', 'vision', 'terminal']:")
    print(f"    Result: {', '.join(sorted(combined))}")
    
    print("\nCustom Toolset Creation:")
    print("-" * 40)
    create_custom_toolset(
        name="my_custom",
        description="My custom toolset for specific tasks",
        tools=["web_search"],
        includes=["terminal", "vision"]
    )
    custom_info = get_toolset_info("my_custom")
    print("  Created 'my_custom' toolset:")
    print(f"    Description: {custom_info['description']}")
    print(f"    Resolved tools: {', '.join(custom_info['resolved_tools'])}")
