"""
Hermes control client — lightweight module for external tools to control
a running Hermes gateway.

This is the module desloppify (or any external tool) imports to switch
models, list sessions, etc. on a live Hermes instance.

Usage:
    from gateway.hermes_control_client import HermesControl

    ctl = HermesControl()  # auto-discovers port from ~/.hermes/control_api.port

    # Switch model on whichever agent is running
    result = ctl.switch_model("openrouter", "anthropic/claude-sonnet-4")

    # Switch model on a specific session
    result = ctl.switch_model("openrouter", "anthropic/claude-sonnet-4",
                              session_key="agent:main:telegram:12345")

    # List running sessions
    sessions = ctl.list_sessions()

Zero dependencies beyond stdlib (uses urllib, not requests/aiohttp).
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_PORT = 47823
PORT_FILE = os.path.expanduser("~/.hermes/control_api.port")


class HermesControl:
    """Client for the Hermes gateway control API."""

    def __init__(self, host: str = "127.0.0.1", port: Optional[int] = None):
        if port is None:
            port = self._discover_port()
        self.base_url = f"http://{host}:{port}"

    @staticmethod
    def _discover_port() -> int:
        try:
            with open(PORT_FILE) as f:
                return int(f.read().strip())
        except (OSError, ValueError):
            return DEFAULT_PORT

    def _request(self, method: str, path: str, body: dict = None) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"} if data else {},
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read())
        except urllib.error.URLError as e:
            return {"error": f"Cannot reach Hermes control API: {e.reason}"}

    def health(self) -> dict:
        """Check if the control API is running."""
        return self._request("GET", "/health")

    def list_sessions(self) -> dict:
        """List all running agent sessions."""
        return self._request("GET", "/sessions")

    def get_session(self, session_key: str) -> dict:
        """Get info about a specific session."""
        return self._request("GET", f"/sessions/{session_key}")

    def switch_model(
        self,
        provider: str,
        model: str,
        session_key: str = "_any",
        reason: str = "",
    ) -> dict:
        """Switch the model on a running agent session.

        Args:
            provider: Provider ID (e.g., "openrouter", "anthropic")
            model: Model ID (e.g., "anthropic/claude-sonnet-4")
            session_key: Session to switch. "_any" switches the first running agent.
            reason: Optional reason string (logged by Hermes).

        Returns:
            Dict with success/failure and previous/current model info.
        """
        return self._request("POST", f"/sessions/{session_key}/switch-model", {
            "provider": provider,
            "model": model,
            "reason": reason or "desloppify",
        })

    def is_available(self) -> bool:
        """Check if a Hermes gateway with control API is reachable."""
        try:
            result = self.health()
            return result.get("status") == "ok"
        except Exception:
            return False
