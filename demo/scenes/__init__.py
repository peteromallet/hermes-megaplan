"""Scene registry, PlaybackContext, and base protocol."""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

from rich.console import Console

from hermes_cli.skin_engine import SkinConfig, load_skin


# ── Timing manifest ─────────────────────────────────────────────────────

@dataclass
class TimingMarker:
    """A single named timestamp in the recording."""
    name: str
    t: float


@dataclass
class SceneTiming:
    """Timing data for one scene."""
    index: int
    scene_type: str  # "conversation" | "action"
    action: Optional[str] = None
    start_t: float = 0.0
    end_t: float = 0.0
    markers: Dict[str, float] = field(default_factory=dict)


@dataclass
class TimingManifest:
    """Full timing data for a recording session."""
    scenes: List[SceneTiming] = field(default_factory=list)
    total_duration: float = 0.0

    def add_scene(self, scene: SceneTiming):
        self.scenes.append(scene)

    def finalize(self):
        if self.scenes:
            self.total_duration = max(s.end_t for s in self.scenes)

    def to_dict(self) -> dict:
        result = {"scenes": [], "total_duration": self.total_duration}
        for s in self.scenes:
            entry: Dict[str, Any] = {
                "index": s.index,
                "type": s.scene_type,
                "start_t": round(s.start_t, 3),
                "end_t": round(s.end_t, 3),
            }
            if s.action:
                entry["action"] = s.action
            if s.markers:
                entry["markers"] = {k: round(v, 3) for k, v in s.markers.items()}
            result["scenes"].append(entry)
        return result

    def save(self, path: Path):
        path.write_text(json.dumps(self.to_dict(), indent=2))


# ── ANSI helpers (skin-aware) ───────────────────────────────────────────

def hex_to_ansi(hex_color: str) -> str:
    """Convert #RRGGBB to ANSI 24-bit foreground escape."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return ""
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


_BOLD = "\033[1m"
_DIM = "\033[2m"
_RST = "\033[0m"


# ── Playback context ───────────────────────────────────────────────────

@dataclass
class PlaybackContext:
    """Shared state passed to every scene handler during playback."""

    skin: SkinConfig
    console: Console
    typing_speed: float = 0.04
    pause_between: float = 1.0
    scene_index: int = 0
    recording_start: float = 0.0  # monotonic time of recording start
    timing: Optional[TimingManifest] = None

    # ── skin ANSI shortcuts ──────────────────────────────────────────

    @property
    def ansi_prompt(self) -> str:
        return hex_to_ansi(self.skin.get_color("prompt", "#FFF8DC"))

    @property
    def ansi_banner_title(self) -> str:
        return hex_to_ansi(self.skin.get_color("banner_title", "#FFD700"))

    @property
    def ansi_banner_border(self) -> str:
        return hex_to_ansi(self.skin.get_color("banner_border", "#CD7F32"))

    @property
    def ansi_banner_accent(self) -> str:
        return hex_to_ansi(self.skin.get_color("banner_accent", "#FFBF00"))

    @property
    def ansi_banner_dim(self) -> str:
        return hex_to_ansi(self.skin.get_color("banner_dim", "#B8860B"))

    @property
    def ansi_banner_text(self) -> str:
        return hex_to_ansi(self.skin.get_color("banner_text", "#FFF8DC"))

    # ── timing helpers ───────────────────────────────────────────────

    def now(self) -> float:
        """Seconds since recording started."""
        return time.monotonic() - self.recording_start

    def mark(self, scene_timing: SceneTiming, name: str):
        """Record a named timing marker on the current scene."""
        scene_timing.markers[name] = self.now()


# ── Scene handler protocol ──────────────────────────────────────────────

class SceneHandler(Protocol):
    """Protocol for scene handler functions."""

    def __call__(self, scene: Any, ctx: PlaybackContext) -> None: ...


# ── Scene registry ──────────────────────────────────────────────────────

_registry: Dict[str, SceneHandler] = {}


def register(scene_type: str) -> Callable:
    """Decorator to register a scene handler."""
    def decorator(fn: SceneHandler) -> SceneHandler:
        _registry[scene_type] = fn
        return fn
    return decorator


def get_handler(scene_type: str) -> Optional[SceneHandler]:
    """Look up a registered scene handler."""
    return _registry.get(scene_type)


def dispatch(scene: Any, ctx: PlaybackContext) -> None:
    """Dispatch a parsed scene to its handler."""
    from demo.schema import ActionScene, ConversationScene

    if isinstance(scene, ActionScene):
        handler = get_handler(f"action:{scene.action}")
        if handler is None:
            handler = get_handler("action")
        if handler:
            handler(scene, ctx)
    elif isinstance(scene, ConversationScene):
        handler = get_handler("conversation")
        if handler:
            handler(scene, ctx)
