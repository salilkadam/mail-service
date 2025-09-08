"""Test configuration."""

import pytest
from app.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly."""
    assert settings.app_name == "Mail Service"
    assert settings.app_version == "0.1.0"
    assert settings.postfix_host is not None
    assert settings.postfix_port == 25
