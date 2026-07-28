from app.auth import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_and_verify_roundtrip():
    plain = "supersecret123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_roundtrip():
    user_id = "abc-123"
    token = create_access_token(subject=user_id)

    decoded_subject = decode_access_token(token)

    assert decoded_subject == user_id


def test_invalid_token_returns_none():
    assert decode_access_token("not.a.valid.token") is None
