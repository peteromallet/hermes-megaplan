"""Camera system: resolve keyframes from screenplay + timing, interpolate zoom/pan.

Camera coordinates:
- x, y: normalized 0.0–1.0 (viewport center position)
- zoom: multiplier (1.0 = full frame, 2.0 = 2x zoom)

Used by compositor.py to crop each frame during encoding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from demo.schema import ConversationScene, ActionScene, Screenplay
from demo.scenes import TimingManifest


@dataclass
class CameraKeyframe:
    """Resolved camera keyframe with absolute timestamp."""
    t: float       # Absolute time in seconds
    zoom: float    # 1.0 = full frame
    x: float       # 0.0–1.0
    y: float       # 0.0–1.0
    duration: float  # Transition time to reach this state
    ease: str      # "linear", "ease-in", "ease-out", "ease-in-out"


def resolve_keyframes(
    screenplay: Screenplay,
    manifest: TimingManifest,
) -> List[CameraKeyframe]:
    """Resolve camera directives from screenplay scenes against timing manifest.

    Returns a sorted list of CameraKeyframes with absolute timestamps.
    """
    keyframes: List[CameraKeyframe] = []
    scenes = screenplay.parsed_scenes()

    for i, scene in enumerate(scenes):
        if i >= len(manifest.scenes):
            break
        timing = manifest.scenes[i]

        if isinstance(scene, ConversationScene):
            if scene.camera:
                t = _resolve_marker_time(scene.camera.at, timing)
                if t is not None:
                    keyframes.append(CameraKeyframe(
                        t=t, zoom=scene.camera.zoom,
                        x=scene.camera.x, y=scene.camera.y,
                        duration=scene.camera.duration, ease=scene.camera.ease,
                    ))
            if scene.camera_response:
                t = _resolve_marker_time(scene.camera_response.at, timing)
                if t is None:
                    t = timing.markers.get("response_start", timing.end_t)
                if t is not None:
                    keyframes.append(CameraKeyframe(
                        t=t, zoom=scene.camera_response.zoom,
                        x=scene.camera_response.x, y=scene.camera_response.y,
                        duration=scene.camera_response.duration,
                        ease=scene.camera_response.ease,
                    ))

        elif isinstance(scene, ActionScene) and scene.action == "camera":
            t = timing.markers.get("camera", timing.start_t)
            keyframes.append(CameraKeyframe(
                t=t,
                zoom=timing.markers.get("_zoom", 1.0),
                x=timing.markers.get("_x", 0.5),
                y=timing.markers.get("_y", 0.5),
                duration=timing.markers.get("_duration", 0.5),
                ease=scene.ease or "ease-in-out",
            ))

    keyframes.sort(key=lambda k: k.t)

    # Ensure there's always a starting keyframe at t=0
    if not keyframes or keyframes[0].t > 0.01:
        keyframes.insert(0, CameraKeyframe(
            t=0.0, zoom=1.0, x=0.5, y=0.5, duration=0.0, ease="linear",
        ))

    return keyframes


def _resolve_marker_time(marker: str, timing) -> Optional[float]:
    """Resolve a marker name to an absolute time from scene timing."""
    if marker == "scene_start":
        return timing.start_t
    if marker == "scene_end":
        return timing.end_t
    return timing.markers.get(marker, timing.start_t)


# ── Easing functions ────────────────────────────────────────────────────

def _ease(t: float, ease_type: str) -> float:
    """Apply easing to normalized t (0.0–1.0)."""
    t = max(0.0, min(1.0, t))
    if ease_type == "linear":
        return t
    elif ease_type == "ease-in":
        return t * t
    elif ease_type == "ease-out":
        return 1.0 - (1.0 - t) * (1.0 - t)
    elif ease_type == "ease-in-out":
        # Smoothstep
        return t * t * (3.0 - 2.0 * t)
    return t


def interpolate_keyframes(
    keyframes: List[CameraKeyframe], t: float
) -> tuple[float, float, float]:
    """Interpolate zoom, x, y at time t given sorted keyframes."""
    if not keyframes:
        return 1.0, 0.5, 0.5

    # Before first keyframe
    if t <= keyframes[0].t:
        kf = keyframes[0]
        return kf.zoom, kf.x, kf.y

    # Find the active transition
    for i in range(1, len(keyframes)):
        kf = keyframes[i]
        prev = keyframes[i - 1]
        transition_start = kf.t - kf.duration
        if t <= kf.t:
            if t < transition_start:
                return prev.zoom, prev.x, prev.y
            # In transition
            progress = (t - transition_start) / kf.duration if kf.duration > 0 else 1.0
            eased = _ease(progress, kf.ease)
            zoom = prev.zoom + (kf.zoom - prev.zoom) * eased
            x = prev.x + (kf.x - prev.x) * eased
            y = prev.y + (kf.y - prev.y) * eased
            return zoom, x, y

    # After last keyframe
    last = keyframes[-1]
    return last.zoom, last.x, last.y
