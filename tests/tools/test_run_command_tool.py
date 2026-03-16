import json
import urllib.error
from unittest.mock import patch, mock_open, MagicMock

from tools.run_command_tool import _discover_port, _run_command, _handle_run_command, _check_run_command

def test_discover_port_success():
    with patch("builtins.open", mock_open(read_data="50000")):
        assert _discover_port() == 50000

def test_discover_port_failure():
    with patch("builtins.open", mock_open()) as m_open:
        m_open.side_effect = FileNotFoundError
        assert _discover_port() == 47823

def test_run_command_success():
    with patch("tools.run_command_tool._discover_port", return_value=50000):
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({"success": True}).encode("utf-8")
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            result = json.loads(_run_command("/status"))
            assert result["success"] is True

def test_run_command_http_error():
    with patch("tools.run_command_tool._discover_port", return_value=50000):
        error = urllib.error.HTTPError(url="", code=400, msg="Bad Request", hdrs={}, fp=None)
        error.read = MagicMock(return_value=b'{"error": "bad cmd"}')
        with patch("urllib.request.urlopen", side_effect=error):
            result = json.loads(_run_command("/invalid"))
            assert result["error"] == "bad cmd"

def test_run_command_url_error():
    with patch("tools.run_command_tool._discover_port", return_value=50000):
        error = urllib.error.URLError("Connection refused")
        with patch("urllib.request.urlopen", side_effect=error):
            result = json.loads(_run_command("/status"))
            assert "Control API not reachable" in result["error"]

def test_handle_run_command_missing():
    result = json.loads(_handle_run_command({}))
    assert result["error"] == "'command' is required"

def test_handle_run_command_invalid_mode():
    result = json.loads(_handle_run_command({"command": "/status", "mode": "invalid"}))
    assert "Invalid mode" in result["error"]

def test_check_run_command():
    with patch.dict("os.environ", {"HERMES_SELF_COMMAND": "1"}):
        assert _check_run_command() is True
    with patch.dict("os.environ", {"HERMES_SELF_COMMAND": "0"}):
        assert _check_run_command() is False
