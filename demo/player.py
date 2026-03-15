#!/usr/bin/env python3
"""Hermes Agent demo player — plays scripted terminal sessions.

Loads a YAML screenplay, parses it into typed scenes, and dispatches
each scene to registered handlers via the scene registry.

Supports skin engine integration for theming and emits a timing manifest
for the camera post-processing pipeline.

Usage:
    python -m demo scripts/example.yaml --play
    python -m demo scripts/example.yaml -o output.mp4
    python demo/player.py demo/scripts/example.yaml   # legacy compat
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console

from hermes_cli.skin_engine import load_skin

from demo.schema import Screenplay
from demo.scenes import (
    PlaybackContext, TimingManifest, _RST,
    dispatch,
)
# Import scene modules to trigger @register decorators
import demo.scenes.conversation  # noqa: F401
import demo.scenes.action  # noqa: F401


def load_screenplay(
    path: str,
    skin_override: Optional[str] = None,
    typing_speed_override: Optional[float] = None,
) -> Screenplay:
    """Load and validate a YAML screenplay file."""
    with open(path) as f:
        raw = yaml.safe_load(f)

    screenplay = Screenplay(**raw)

    # Store source path for pipeline to reference
    screenplay._source_path = Path(path).resolve()  # type: ignore[attr-defined]

    if skin_override:
        screenplay.skin = skin_override
    if typing_speed_override is not None:
        screenplay.typing_speed = typing_speed_override

    return screenplay


def play(
    screenplay: Screenplay,
    timing_path: Optional[Path] = None,
) -> None:
    """Play a screenplay in the terminal.

    Args:
        screenplay: Parsed screenplay to play.
        timing_path: If set, write timing manifest JSON here after playback.
    """
    skin = load_skin(screenplay.skin)
    console = Console()

    timing = TimingManifest() if timing_path else None

    ctx = PlaybackContext(
        skin=skin,
        console=console,
        typing_speed=screenplay.typing_speed,
        pause_between=screenplay.pause_between,
        recording_start=time.monotonic(),
        timing=timing,
    )

    scenes = screenplay.parsed_scenes()

    for i, scene in enumerate(scenes):
        ctx.scene_index = i
        dispatch(scene, ctx)

    # Final prompt to show it's still "alive"
    prompt_color = ctx.ansi_prompt
    prompt_symbol = skin.get_branding("prompt_symbol", "❯ ")
    sys.stdout.write(f"\n{prompt_color}{prompt_symbol}{_RST}")
    sys.stdout.flush()
    time.sleep(2)
    sys.stdout.write("\n")

    # Write timing manifest
    if timing and timing_path:
        timing.finalize()
        timing.save(timing_path)


# ── Legacy CLI entry point (python demo/player.py script.yaml) ─────────

def main():
    parser = argparse.ArgumentParser(description="Hermes Agent demo player")
    parser.add_argument("script", help="Path to YAML screenplay file")
    parser.add_argument("--typing-speed", type=float, default=None,
                        help="Base typing speed in seconds per character")
    parser.add_argument("--skin", default=None, help="Skin name override")
    args = parser.parse_args()

    screenplay = load_screenplay(
        args.script,
        skin_override=args.skin,
        typing_speed_override=args.typing_speed,
    )

    try:
        play(screenplay)
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{_RST}")
        sys.exit(0)


if __name__ == "__main__":
    main()
