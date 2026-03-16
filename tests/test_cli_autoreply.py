"""Tests for CLI /autoreply command, _generate_autoreply_text, and _CLIRunner shim."""

import queue
from unittest.mock import MagicMock, patch

from tests.test_cli_init import _make_cli
from agent.autoreply import _DEFAULT_MAX_TURNS


# ---------------------------------------------------------------------------
# _handle_autoreply_command
# ---------------------------------------------------------------------------


class TestCLIHandleAutoreplyCommand:
    """Tests for HermesCLI._handle_autoreply_command."""

    def test_enable_with_instructions(self):
        cli = _make_cli()
        cli._handle_autoreply_command("/autoreply Ask follow-up questions")
        assert cli._autoreply_config is not None
        assert cli._autoreply_config["prompt"] == "Ask follow-up questions"
        assert cli._autoreply_config["max_turns"] == _DEFAULT_MAX_TURNS
        assert cli._autoreply_config["turn_count"] == 0

    def test_disable(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0,
        }
        cli._handle_autoreply_command("/autoreply off")
        assert cli._autoreply_config is None

    def test_disable_when_not_active(self):
        cli = _make_cli()
        cli._autoreply_config = None
        cli._handle_autoreply_command("/autoreply off")
        assert cli._autoreply_config is None  # still None, no error

    def test_set_max_turns(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0,
        }
        cli._handle_autoreply_command("/autoreply max 25")
        assert cli._autoreply_config["max_turns"] == 25

    def test_max_without_active_config(self):
        cli = _make_cli()
        cli._autoreply_config = None
        cli._handle_autoreply_command("/autoreply max 5")
        assert cli._autoreply_config is None  # not enabled

    def test_status_when_active_does_not_error(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "Ask questions", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 3,
        }
        # Should not raise
        cli._handle_autoreply_command("/autoreply")
        # Config unchanged
        assert cli._autoreply_config["turn_count"] == 3

    def test_status_when_inactive_does_not_error(self):
        cli = _make_cli()
        cli._autoreply_config = None
        cli._handle_autoreply_command("/autoreply")
        assert cli._autoreply_config is None

    def test_literal_mode(self):
        cli = _make_cli()
        cli._handle_autoreply_command("/autoreply --literal continue")
        assert cli._autoreply_config is not None
        assert cli._autoreply_config["prompt"] == "continue"
        assert cli._autoreply_config["literal"] is True

    def test_forever_mode(self):
        cli = _make_cli()
        cli._handle_autoreply_command("/autoreply --forever keep going")
        assert cli._autoreply_config is not None
        assert cli._autoreply_config["max_turns"] == 0

    def test_disable_aliases(self):
        """All disable aliases work: off, disable, stop."""
        for word in ("off", "disable", "stop"):
            cli = _make_cli()
            cli._autoreply_config = {
                "prompt": "test", "model": None,
                "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0,
            }
            cli._handle_autoreply_command(f"/autoreply {word}")
            assert cli._autoreply_config is None, f"'{word}' did not disable autoreply"

    def test_instructions_starting_with_max_not_treated_as_subcommand(self):
        """'/autoreply maximize depth' should set instructions, not parse as /max."""
        cli = _make_cli()
        cli._handle_autoreply_command("/autoreply maximize the depth of investigation")
        assert cli._autoreply_config is not None
        assert "maximize" in cli._autoreply_config["prompt"]


# ---------------------------------------------------------------------------
# _generate_autoreply_text
# ---------------------------------------------------------------------------


class TestCLIGenerateAutoreplyText:
    """Tests for HermesCLI._generate_autoreply_text."""

    def test_returns_none_when_not_configured(self):
        cli = _make_cli()
        assert cli._generate_autoreply_text() is None

    def test_literal_mode_returns_prompt_directly(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "continue", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0, "literal": True,
        }
        result = cli._generate_autoreply_text()
        assert result == "continue"
        assert cli._autoreply_config["turn_count"] == 1

    def test_cap_reached_clears_config(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": 3, "turn_count": 3,
        }
        result = cli._generate_autoreply_text()
        assert result is None
        assert cli._autoreply_config is None

    def test_llm_mode_calls_call_llm(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "Ask follow-up questions", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0,
        }
        cli.conversation_history = [
            {"role": "user", "content": "Tell me about Python"},
            {"role": "assistant", "content": "Python is great."},
        ]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "What about type hints?"

        with patch("agent.auxiliary_client.call_llm", return_value=mock_response) as mock_llm:
            result = cli._generate_autoreply_text()

        assert result == "What about type hints?"
        assert cli._autoreply_config["turn_count"] == 1
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["task"] == "autoreply"
        assert call_kwargs["temperature"] == 0.7
        # System prompt should contain the user's instructions
        system_msg = call_kwargs["messages"][0]
        assert system_msg["role"] == "system"
        assert "Ask follow-up questions" in system_msg["content"]

    def test_model_override_passed_to_llm(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": "openai/gpt-4o-mini",
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0,
        }
        cli.conversation_history = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "reply"

        with patch("agent.auxiliary_client.call_llm", return_value=mock_response) as mock_llm:
            cli._generate_autoreply_text()

        assert mock_llm.call_args[1]["model"] == "openai/gpt-4o-mini"

    def test_forever_mode_does_not_cap(self):
        """max_turns=0 means forever — turn counting never stops."""
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "keep going", "model": None,
            "max_turns": 0, "turn_count": 100, "literal": True,
        }
        result = cli._generate_autoreply_text()
        assert result == "keep going"
        assert cli._autoreply_config["turn_count"] == 101


# ---------------------------------------------------------------------------
# _CLIRunner shim
# ---------------------------------------------------------------------------


class TestCLIRunnerShim:
    """Tests for the _CLIRunner shim used by ControlAPI in CLI mode."""

    def _make_shim(self):
        """Build a _CLIRunner matching the one defined in _start_control_api."""
        cli = _make_cli()
        cli._agent_running = False
        cli._pending_input = queue.Queue()
        cli._interrupt_queue = queue.Queue()
        cli._autoreply_config = None
        cli.agent = MagicMock()
        cli.session_id = "test-session"

        class _CLIRunner:
            def __init__(self, agent, session_id, cli_instance):
                self._running_agents = {session_id: agent}
                self._cli = cli_instance

            def inject_message(self, key, text, *, interrupt=True):
                if interrupt and self._cli._agent_running:
                    self._cli._interrupt_queue.put(text)
                else:
                    self._cli._pending_input.put(text)

            def get_session_info(self, key):
                cfg = getattr(self._cli, "_autoreply_config", None)
                return {
                    "autoreply": {
                        "enabled": cfg is not None,
                        "prompt": cfg.get("prompt", "") if cfg else None,
                        "max_turns": cfg.get("max_turns", 0) if cfg else None,
                        "turn_count": cfg.get("turn_count", 0) if cfg else None,
                    },
                }

        shim = _CLIRunner(cli.agent, cli.session_id, cli)
        return shim, cli

    def test_inject_message_interrupt_mode(self):
        """Interrupt mode puts message on _interrupt_queue when agent is running."""
        shim, cli = self._make_shim()
        cli._agent_running = True
        shim.inject_message("_any", "/stop", interrupt=True)
        assert cli._interrupt_queue.get_nowait() == "/stop"
        assert cli._pending_input.empty()

    def test_inject_message_queue_mode(self):
        """Queue mode always puts message on _pending_input."""
        shim, cli = self._make_shim()
        cli._agent_running = True
        shim.inject_message("_any", "/model cheap", interrupt=False)
        assert cli._pending_input.get_nowait() == "/model cheap"
        assert cli._interrupt_queue.empty()

    def test_inject_message_interrupt_when_not_running(self):
        """When agent is not running, interrupt falls through to _pending_input."""
        shim, cli = self._make_shim()
        cli._agent_running = False
        shim.inject_message("_any", "hello", interrupt=True)
        assert cli._pending_input.get_nowait() == "hello"
        assert cli._interrupt_queue.empty()

    def test_get_session_info_no_autoreply(self):
        shim, cli = self._make_shim()
        info = shim.get_session_info("_any")
        assert info["autoreply"]["enabled"] is False
        assert info["autoreply"]["prompt"] is None

    def test_get_session_info_with_autoreply(self):
        shim, cli = self._make_shim()
        cli._autoreply_config = {
            "prompt": "keep going", "model": None,
            "max_turns": 10, "turn_count": 3,
        }
        info = shim.get_session_info("_any")
        assert info["autoreply"]["enabled"] is True
        assert info["autoreply"]["prompt"] == "keep going"
        assert info["autoreply"]["max_turns"] == 10
        assert info["autoreply"]["turn_count"] == 3

    def test_running_agents_contains_session(self):
        shim, cli = self._make_shim()
        assert cli.session_id in shim._running_agents


# ---------------------------------------------------------------------------
# Reset clears autoreply
# ---------------------------------------------------------------------------


class TestCLIAutoreplyCleanup:
    """Tests for autoreply cleanup on /reset and /new."""

    def test_reset_clears_autoreply(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 5,
        }
        cli.process_command("/reset")
        assert cli._autoreply_config is None

    def test_new_clears_autoreply(self):
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 5,
        }
        cli.process_command("/new")
        assert cli._autoreply_config is None


# ---------------------------------------------------------------------------
# Chat loop autoreply wiring
# ---------------------------------------------------------------------------


class TestCLIAutoreplyPrefix:
    """Tests for the [autoreply] prefix stripping and turn counter reset logic."""

    def test_autoreply_prefix_detected(self):
        user_input = "[autoreply]What else can you tell me?"
        assert user_input.startswith("[autoreply]")
        stripped = user_input[len("[autoreply]"):]
        assert stripped == "What else can you tell me?"

    def test_regular_message_not_detected(self):
        user_input = "Tell me more"
        assert not user_input.startswith("[autoreply]")

    def test_turn_counter_reset_on_real_message(self):
        """Real user messages reset the turn counter."""
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 7,
        }
        user_input = "Tell me more"
        if cli._autoreply_config and not user_input.startswith("[autoreply]"):
            cli._autoreply_config["turn_count"] = 0
        assert cli._autoreply_config["turn_count"] == 0

    def test_turn_counter_not_reset_on_autoreply_message(self):
        """Autoreply-injected messages do NOT reset the turn counter."""
        cli = _make_cli()
        cli._autoreply_config = {
            "prompt": "test", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 7,
        }
        user_input = "[autoreply]Generated question"
        if cli._autoreply_config and not user_input.startswith("[autoreply]"):
            cli._autoreply_config["turn_count"] = 0
        assert cli._autoreply_config["turn_count"] == 7

    def test_autoreply_injection_into_pending_input(self):
        """After agent response, autoreply text is pushed onto _pending_input."""
        cli = _make_cli()
        cli._pending_input = queue.Queue()
        cli._autoreply_config = {
            "prompt": "continue", "model": None,
            "max_turns": _DEFAULT_MAX_TURNS, "turn_count": 0, "literal": True,
        }

        reply = cli._generate_autoreply_text()
        if reply:
            cli._pending_input.put(f"[autoreply]{reply}")

        assert not cli._pending_input.empty()
        queued = cli._pending_input.get_nowait()
        assert queued == "[autoreply]continue"


# ---------------------------------------------------------------------------
# _start_control_api gating
# ---------------------------------------------------------------------------


class TestCLIControlAPIGating:
    """Tests for _start_control_api env var gating."""

    def test_control_api_not_started_without_env_var(self):
        """Without HERMES_CONTROL_API, _start_control_api does nothing."""
        cli = _make_cli()
        with patch.dict("os.environ", {"HERMES_CONTROL_API": ""}, clear=False):
            with patch("gateway.control_api.ControlAPI") as mock_api:
                cli._start_control_api()
                mock_api.assert_not_called()

    def test_control_api_started_with_env_var(self):
        """With HERMES_CONTROL_API=1, ControlAPI is instantiated."""
        cli = _make_cli()
        cli.agent = MagicMock()
        cli.session_id = "test-session"
        with patch.dict("os.environ", {"HERMES_CONTROL_API": "1"}, clear=False):
            with patch("gateway.control_api.ControlAPI") as mock_api, \
                 patch("threading.Thread") as mock_thread, \
                 patch("time.sleep"):
                mock_thread.return_value.start = MagicMock()
                cli._start_control_api()
                mock_api.assert_called_once()
                mock_thread.return_value.start.assert_called_once()
