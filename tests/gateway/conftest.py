"""Pytest fixtures specific to gateway tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from gateway.run import GatewayRunner


@pytest.fixture
def make_runner():
    """Create a test GatewayRunner without calling __init__ (avoids heavy setup).

    Centralizes the fragile object.__new__ + setattr pattern. When GatewayRunner.__init__
    gains new attributes, update this one place instead of 9+ test files.
    """
    def _make(**overrides):
        runner = object.__new__(GatewayRunner)
        
        defaults = {
            "config": MagicMock(),
            "adapters": {},
            "_adapters": {},
            "session_store": MagicMock(),
            "_session_store": MagicMock(),
            "_session_db": None,
            "_running_agents": {},
            "_reasoning_config": None,
            "_prefill_messages": None,
            "_fallback_model": None,
            "_provider_routing": {},
            "pairing_store": MagicMock(),
            "hooks": MagicMock(emit=AsyncMock()),
            "delivery_router": MagicMock(),
            "logger": MagicMock(),
            "_honcho_managers": {},
            "_honcho_configs": {},
            "_autoreply_configs": {},
            "_pending_approvals": {},
            "_show_reasoning": False,
            "_ephemeral_system_prompt": None,
        }
        defaults.update(overrides)
        
        for attr, val in defaults.items():
            setattr(runner, attr, val)
        
        # Some tests expect specific methods to be mocked
        if not hasattr(runner, "_handle_message"):
            runner._handle_message = AsyncMock()
        if not hasattr(runner, "_is_user_authorized"):
            runner._is_user_authorized = MagicMock(return_value=True)
        
        return runner
    
    return _make
