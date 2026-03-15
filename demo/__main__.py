"""CLI entry point: python -m demo script.yaml [-o out.mp4] [--play] [--skin ares]."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="python -m demo",
        description="Hermes Agent demo video framework",
    )
    parser.add_argument(
        "script", help="Path to YAML screenplay file",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output video path (e.g. output.mp4). If omitted, defaults to --play mode.",
    )
    parser.add_argument(
        "--play", action="store_true",
        help="Preview in terminal (no recording)",
    )
    parser.add_argument(
        "--skin", default=None,
        help="Override skin name (e.g. ares, mono, slate)",
    )
    parser.add_argument(
        "--typing-speed", type=float, default=None,
        help="Override base typing speed (seconds per character)",
    )
    parser.add_argument(
        "--timing", type=Path, default=None,
        help="Write timing manifest JSON to this path (used internally by pipeline)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print pipeline commands without executing them",
    )
    args = parser.parse_args()

    # If neither --output nor --play, default to --play
    if args.output is None and not args.play:
        args.play = True

    # Load screenplay
    from demo.player import load_screenplay
    screenplay = load_screenplay(
        args.script,
        skin_override=args.skin,
        typing_speed_override=args.typing_speed,
    )

    if args.play:
        # Terminal preview mode
        from demo.player import play
        try:
            play(screenplay, timing_path=args.timing)
        except KeyboardInterrupt:
            sys.stdout.write("\033[0m\n")
            sys.exit(0)
    else:
        # Full pipeline mode
        from demo.pipeline import run_pipeline
        run_pipeline(
            screenplay=screenplay,
            output_path=args.output,
            skin_override=args.skin,
            typing_speed_override=args.typing_speed,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
