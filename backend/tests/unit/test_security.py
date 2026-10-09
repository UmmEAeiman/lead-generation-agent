from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    hashed = hash_password("s3cret-pass")
    assert hashed != "s3cret-pass"
    assert verify_password("s3cret-pass", hashed)
    assert not verify_password("wrong", hashed)


def test_verify_password_bad_hash() -> None:
    assert not verify_password("anything", "not-a-bcrypt-hash")


def test_token_roundtrip() -> None:
    token = create_access_token("user-123", {"role": "owner"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "owner"


def test_invalid_token_raises() -> None:
    try:
        decode_access_token("garbage.token.value")
    except TokenError:
        pass
    else:
        raise AssertionError("Expected TokenError for invalid token")
