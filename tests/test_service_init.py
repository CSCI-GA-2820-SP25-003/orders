import pytest
from unittest.mock import patch
from service import create_app

"""Unit tests for service initialization."""


def test_create_app_exception_handling(capfd):
    """Test if exception handling is triggered during app initialization"""

    # db.create_all while it raises an exception
    with patch("service.models.db.create_all", side_effect=Exception("DB Error")):
        with pytest.raises(SystemExit):  # Calls sys.exit(4)
            create_app()

    # Capture error and check if the critical log message is present
    captured = capfd.readouterr()
    assert "DB Error: Cannot continue" in captured.err
