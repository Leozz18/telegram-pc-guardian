from guardian.auth import CommandAuthorizer


def test_unallowlisted_chat_is_denied():
    auth = CommandAuthorizer(42)
    assert not auth.inspect(7, "/status").allowed


def test_sensitive_command_requires_confirmation():
    auth = CommandAuthorizer(42, ttl_seconds=60)
    request = auth.inspect(42, "/shutdown")
    assert request.allowed and request.needs_confirmation
    assert auth.inspect(42, "/confirm wrong").allowed is False
    done = auth.inspect(42, f"/confirm {request.confirmation_code}")
    assert done.allowed and done.action == "shutdown"


def test_confirmation_is_single_use():
    auth = CommandAuthorizer(42)
    request = auth.inspect(42, "/screenshot")
    assert auth.inspect(42, f"/confirm {request.confirmation_code}").allowed
    assert not auth.inspect(42, f"/confirm {request.confirmation_code}").allowed


def test_status_does_not_need_confirmation():
    decision = CommandAuthorizer(42).inspect(42, "/status")
    assert decision.allowed and decision.action == "status"
