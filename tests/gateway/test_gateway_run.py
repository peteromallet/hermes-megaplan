"""Dedicated tests for gateway/run.py core pipeline: GatewayRunner._handle_message.

Focuses on command dispatch routing, agent launch paths, error handling, and
the main message processing flow. Complements the per-command test files.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from gateway.platforms.base import MessageEvent, MessageType
from gateway.config import Platform


@pytest.mark.asyncio
async def test_help_command_dispatches(make_runner):
    """Quick commands like /help are dispatched to their _handle_*_command methods."""
    runner = make_runner()
    runner._handle_help_command = AsyncMock(return_value="Help text here~")
    
    event = MessageEvent(
        text="/help",
        message_type=MessageType.TEXT,
        source=MagicMock(platform=Platform.TELEGRAM, chat_id="123", user_id="u1"),
    )
    
    result = await runner._handle_message(event)
    
    runner._handle_help_command.assert_called_once_with(event)
    assert result == "Help text here~"


@pytest.mark.asyncio
async def test_model_command_dispatches(make_runner):
    """/model command is dispatched to handler."""
    runner = make_runner()
    runner._handle_model_command = AsyncMock(return_value="Model updated~")
    
    event = MessageEvent(
        text="/model gpt-4o",
        message_type=MessageType.TEXT,
        source=MagicMock(platform=Platform.TELEGRAM, chat_id="123", user_id="u1"),
    )
    
    result = await runner._handle_message(event)
    
    runner._handle_model_command.assert_called_once_with(event)
    assert result == "Model updated~"


@pytest.mark.asyncio
async def test_stop_command_dispatches(make_runner):
    """/stop command is dispatched to handler."""
    runner = make_runner()
    runner._handle_stop_command = AsyncMock(return_value="Stopped~")
    
    event = MessageEvent(
        text="/stop",
        message_type=MessageType.TEXT,
        source=MagicMock(platform=Platform.TELEGRAM, chat_id="123", user_id="u1"),
    )
    
    result = await runner._handle_message(event)
    
    runner._handle_stop_command.assert_called_once_with(event)
    assert result == "Stopped~"


@pytest.mark.asyncio
async def test_unauthorized_user_gets_pairing_code(make_runner):
    """Unauthorized DM users receive pairing code prompt."""
    pairing_store = MagicMock(
        generate_code=MagicMock(return_value="ABC123")
    )
    runner = make_runner(pairing_store=pairing_store)
    runner.adapters = {Platform.TELEGRAM: MagicMock(send=AsyncMock())}
    
    event = MessageEvent(
        text="hello",
        message_type=MessageType.TEXT,
        source=MagicMock(
            platform=Platform.TELEGRAM,
            chat_type="dm",
            chat_id="123",
            user_id="unknown",
            user_name="stranger"
        ),
    )
    
    with patch.object(runner, "_is_user_authorized", return_value=False):
        result = await runner._handle_message(event)
    
    assert result is None
    pairing_store.generate_code.assert_called()
    runner.adapters[Platform.TELEGRAM].send.assert_called()


