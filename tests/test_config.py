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


def test_dotenv_is_loaded_without_overriding_explicit_environment(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "TELEGRAM_BOT_TOKEN=123:from-file\n"
        "TELEGRAM_ALLOWED_CHAT_ID=99\n"
        "GUARDIAN_RATE_LIMIT_PER_MINUTE=4\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_ALLOWED_CHAT_ID", raising=False)
    settings = Settings.from_env(dotenv_path=dotenv)
    assert settings.bot_token == "123:from-file"
    assert settings.allowed_chat_id == 99
    assert settings.rate_limit_per_minute == 4

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:explicit")
    explicit = Settings.from_env(dotenv_path=dotenv)
    assert explicit.bot_token == "123:explicit"
