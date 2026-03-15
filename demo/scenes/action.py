"""Action scenes: clear, pause, print, banner, type_command, camera."""

from __future__ import annotations

import os
import sys
import time

from rich.panel import Panel

from demo.schema import ActionScene
from demo.scenes import (
    PlaybackContext, SceneTiming, _BOLD, _DIM, _RST,
    register,
)
from demo.scenes.conversation import type_text


# ── Generic action dispatcher ──────────────────────────────────────────

@register("action")
def play_action(scene: ActionScene, ctx: PlaybackContext):
    """Dispatch an action scene to the right sub-handler."""
    handlers = {
        "pause": _action_pause,
        "clear": _action_clear,
        "print": _action_print,
        "banner": _action_banner,
        "type_command": _action_type_command,
        "camera": _action_camera,
    }
    handler = handlers.get(scene.action)
    if handler:
        handler(scene, ctx)


# ── Individual action handlers ─────────────────────────────────────────

def _action_pause(scene: ActionScene, ctx: PlaybackContext):
    scene_timing = SceneTiming(
        index=ctx.scene_index, scene_type="action", action="pause"
    )
    scene_timing.start_t = ctx.now()
    time.sleep(scene.duration or 1.0)
    scene_timing.end_t = ctx.now()
    if ctx.timing:
        ctx.timing.add_scene(scene_timing)


def _action_clear(scene: ActionScene, ctx: PlaybackContext):
    scene_timing = SceneTiming(
        index=ctx.scene_index, scene_type="action", action="clear"
    )
    scene_timing.start_t = ctx.now()
    os.system("clear")
    scene_timing.end_t = ctx.now()
    if ctx.timing:
        ctx.timing.add_scene(scene_timing)


def _action_print(scene: ActionScene, ctx: PlaybackContext):
    scene_timing = SceneTiming(
        index=ctx.scene_index, scene_type="action", action="print"
    )
    scene_timing.start_t = ctx.now()
    text = scene.text or ""
    if scene.color:
        ctx.console.print(f"[{scene.color}]{text}[/]")
    else:
        print(text)
    scene_timing.end_t = ctx.now()
    if ctx.timing:
        ctx.timing.add_scene(scene_timing)


def _action_type_command(scene: ActionScene, ctx: PlaybackContext):
    """Type a raw shell command (not the agent prompt)."""
    scene_timing = SceneTiming(
        index=ctx.scene_index, scene_type="action", action="type_command"
    )
    scene_timing.start_t = ctx.now()

    cmd = scene.command or ""
    prefix = scene.prefix or "$ "

    sys.stdout.write(f"\n{_DIM}{prefix}{_RST}")
    sys.stdout.flush()
    time.sleep(0.3)
    type_text(cmd, speed=ctx.typing_speed, color=f"{_BOLD}")
    time.sleep(0.5)
    sys.stdout.write("\n")
    sys.stdout.flush()

    output = scene.output or ""
    if output:
        for line in output.split("\n"):
            sys.stdout.write(f"{_DIM}{line}{_RST}\n")
            sys.stdout.flush()
            time.sleep(0.05)

    scene_timing.end_t = ctx.now()
    if ctx.timing:
        ctx.timing.add_scene(scene_timing)


def _action_camera(scene: ActionScene, ctx: PlaybackContext):
    """Standalone camera directive — only records timing, no visual output."""
    scene_timing = SceneTiming(
        index=ctx.scene_index, scene_type="action", action="camera"
    )
    scene_timing.start_t = ctx.now()
    scene_timing.markers["camera"] = ctx.now()
    # Store camera params in markers for the camera resolver
    if scene.zoom is not None:
        scene_timing.markers["_zoom"] = scene.zoom
    if scene.x is not None:
        scene_timing.markers["_x"] = scene.x
    if scene.y is not None:
        scene_timing.markers["_y"] = scene.y
    if scene.duration is not None:
        scene_timing.markers["_duration"] = scene.duration
    scene_timing.end_t = ctx.now()
    if ctx.timing:
        ctx.timing.add_scene(scene_timing)


# ── Banner ──────────────────────────────────────────────────────────────

def _action_banner(scene: ActionScene, ctx: PlaybackContext):
    """Print the Hermes welcome banner using skin colors."""
    from rich.table import Table

    scene_timing = SceneTiming(
        index=ctx.scene_index, scene_type="action", action="banner"
    )
    scene_timing.start_t = ctx.now()

    model = scene.model or "nous-hermes-3"
    context_str = scene.context or "128K"
    session_id = scene.session_id or "demo-session"
    tools_count = scene.tools_count or 24
    skills_count = scene.skills_count or 42

    # Color references from skin
    c_border = ctx.skin.get_color("banner_border", "#CD7F32")
    c_title = ctx.skin.get_color("banner_title", "#FFD700")
    c_accent = ctx.skin.get_color("banner_accent", "#FFBF00")
    c_dim = ctx.skin.get_color("banner_dim", "#B8860B")
    c_text = ctx.skin.get_color("banner_text", "#FFF8DC")

    # Use skin's custom banner art if available, else default
    agent_name = ctx.skin.get_branding("agent_name", "Hermes Agent")

    hero = ctx.skin.banner_hero or _default_caduceus(c_border, c_accent, c_title, c_dim)
    logo = ctx.skin.banner_logo or _default_logo(c_title, c_accent, c_border)

    layout = Table.grid(padding=(0, 2))
    layout.add_column("left", justify="center")
    layout.add_column("right", justify="left")

    left = (
        f"\n{hero}\n\n"
        f"[{c_accent}]{model}[/] [dim {c_dim}]\u00b7[/] "
        f"[dim {c_dim}]{context_str} context[/] [dim {c_dim}]\u00b7[/] "
        f"[dim {c_dim}]Nous Research[/]\n"
        f"[dim {c_dim}]Session: {session_id}[/]"
    )

    right_lines = [
        f"[bold {c_accent}]Available Tools[/]",
        f"[dim {c_dim}]core_tools:[/] [{c_text}]terminal, read_file, write_file, patch, search_files[/]",
        f"[dim {c_dim}]web_tools:[/] [{c_text}]web_search, web_extract, web_crawl[/]",
        f"[dim {c_dim}]browser_tools:[/] [{c_text}]browser_navigate, browser_click, browser_type, ...[/]",
        f"[dim {c_dim}]agent_tools:[/] [{c_text}]delegate_task, mixture_of_agents, memory[/]",
        "",
        f"[bold {c_accent}]Available Skills[/]",
        f"[dim {c_dim}]productivity:[/] [{c_text}]email-send, web-search, summarize, ...[/]",
        f"[dim {c_dim}]development:[/] [{c_text}]git-commit, code-review, test-runner, ...[/]",
        "",
        f"[dim {c_dim}]{tools_count} tools \u00b7 {skills_count} skills \u00b7 /help for commands[/]",
    ]
    right = "\n".join(right_lines)
    layout.add_row(left, right)

    ctx.console.print()
    ctx.console.print(logo)
    ctx.console.print()
    ctx.console.print(Panel(
        layout,
        title=f"[bold {c_title}]{agent_name} v0.9.0[/]",
        border_style=c_border,
        padding=(0, 2),
    ))

    scene_timing.end_t = ctx.now()
    if ctx.timing:
        ctx.timing.add_scene(scene_timing)


# ── Default banner art (Hermes caduceus + logo) ────────────────────────

def _default_caduceus(c1: str, c2: str, c3: str, c4: str) -> str:
    """Default Hermes caduceus art with 4-color gradient.

    Colors map: c1=border, c2=accent, c3=title, c4=dim
    Original uses: #CD7F32, #FFBF00, #FFD700, #B8860B
    """
    return (
        f"[{c1}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⣀⣀⠀⢀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c1}]⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣇⠸⣿⣿⠇⣸⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c2}]⠀⢀⣠⣴⣶⠿⠋⣩⡿⣿⡿⠻⣿⡇⢠⡄⢸⣿⠟⢿⣿⢿⣍⠙⠿⣶⣦⣄⡀⠀[/]\n"
        f"[{c2}]⠀⠀⠉⠉⠁⠶⠟⠋⠀⠉⠀⢀⣈⣁⡈⢁⣈⣁⡀⠀⠉⠀⠙⠻⠶⠈⠉⠉⠀⠀[/]\n"
        f"[{c3}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⡿⠛⢁⡈⠛⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c3}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⣦⣤⣈⠁⢠⣴⣿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c2}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠻⢿⣿⣦⡉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c2}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣦⣈⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c1}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⠦⠈⠙⠿⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c1}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣤⡈⠁⢤⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c4}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c4}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠑⢶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c4}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⢰⡆⠈⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c4}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠈⣡⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]\n"
        f"[{c4}]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀[/]"
    )


def _default_logo(c1: str, c2: str, c3: str) -> str:
    """Default HERMES AGENT block logo."""
    return (
        f"[bold {c1}]██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗       █████╗  ██████╗ ███████╗███╗   ██╗████████╗[/]\n"
        f"[bold {c1}]██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝      ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝[/]\n"
        f"[{c2}]███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗█████╗███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║[/]\n"
        f"[{c2}]██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║╚════╝██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║[/]\n"
        f"[{c3}]██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║      ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║[/]\n"
        f"[{c3}]╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝      ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝[/]"
    )
