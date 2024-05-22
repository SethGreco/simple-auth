from fastapi import Request, HTTPException, status
from qftb.service.auth import (
    restrict_ip_address,
    validate_token,
    generate_token,
    auth_user,
)
from qftb.config import settings
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import pytest


# Positive Test Case
def test_restrict_ip_address_allowed():
    # Mock the Request object with an allowed IP address
    req = Mock(spec=Request)
    req.client.host = "192.168.1.1"

    # Set up ALLOWED_IP_ADDRESSES
    settings.ALLOWED_IP_ADDRESSES

    # Call the function and assert that it returns the client IP address
    assert restrict_ip_address(req) == "192.168.1.1"


# Negative Test Case
def test_restrict_ip_address_not_allowed():
    req = Mock(spec=Request)
    req.client.host = "10.0.0.1"

    settings.ALLOWED_IP_ADDRESSES

    try:
        restrict_ip_address(req)
    except HTTPException as e:
        assert e.status_code == status.HTTP_403_FORBIDDEN
        assert e.detail == "Unreachable Host"
    else:
        # If no exception is raised, fail the test
        assert False, "Expected HTTPException not raised"


def test_validate_token_valid():
    # Valid authorization header
    authorization = "Bearer valid_token"

    # Mocking jwt.decode to return without errors
    with patch("qftb.service.auth.jwt.decode"):
        validate_token(authorization)

    # No exception should be raised


def test_validate_token_invalid_token():
    # Valid authorization header but invalid token
    authorization = "Bearer invalid_token"

    # Mocking jwt.decode to raise JWTError
    with patch("qftb.service.auth.jwt.decode", side_effect=JWTError):
        with pytest.raises(HTTPException) as exc_info:
            validate_token(authorization)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


def test_validate_token_invalid_authorization_header():
    # Invalid authorization header
    authorization = "invalid_header"

    # Calling the function and asserting that it raises an HTTPException with status 401
    with pytest.raises(HTTPException) as exc_info:
        validate_token(authorization)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Missing or invalid Authorization header"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


def test_generate_token():
    # Mock user_info and expires_delta
    user_info = {"username": "test_user", "id": 123}
    expires_delta = timedelta(minutes=30)

    # Mock current datetime to a fixed value
    fixed_datetime = datetime.now(timezone.utc)
    with patch("qftb.service.auth.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_datetime

        # Generate token
        token = generate_token(user_info, expires_delta)

    # Decode token and assert payload
    decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert decoded_token["sub"] == user_info["username"]
    assert decoded_token["id"] == user_info["id"]

    # Calculate expected expiration time and assert
    expected_expiration = fixed_datetime + expires_delta
    assert decoded_token["exp"] == int(expected_expiration.timestamp())


def test_auth_user_successful():
    # Mock database session and user object
    mock_db = MagicMock(spec=Session)
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    mock_user.id = 1

    # Mock the ph.verify function from argon2 library
    with patch("argon2.PasswordHasher.verify") as mock_verify:
        # Set the return value of mock_verify to True to simulate successful password verification
        mock_verify.return_value = True

        # Set the hashed password attribute of the mocked user object
        mock_user.hashed_password = "hashed_password"

        # Set up the mock to return the user object
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Call the function and assert the returned dictionary
        assert auth_user("test@example.com", "password", db=mock_db) == {
            "id": 1,
            "username": "test@example.com",
        }
