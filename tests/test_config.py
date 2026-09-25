import pytest

from guardian.config import ConfigurationError, Settings


def env(**overrides):
    values = {"TELEGRAM_BOT_TOKEN": "123:abc", "TELEGRAM_ALLOWED_CHAT_ID": "42"}
    values.update(overrides)
    return values


def test_valid_configuration():
    settings = Settings.from_env(env())
    assert settings.allowed_chat_id == 42
    assert settings.poll_seconds == 3


@pytest.mark.parametrize("name,value", [
    ("TELEGRAM_BOT_TOKEN", ""),
    ("TELEGRAM_ALLOWED_CHAT_ID", "not-a-number"),
    ("GUARDIAN_RATE_LIMIT_PER_MINUTE", "0"),
])
def test_invalid_configuration_is_rejected(name, value):
    with pytest.raises(ConfigurationError):
        Settings.from_env(env(**{name: value}))
