from .utils import *
from ..routers.auth import *
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException, status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(db, test_user.username, "test1234!")
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_authenticated_user = authenticate_user(db, test_user.username, "wrongpassword")
    assert non_authenticated_user is False

    wrong_password_user = authenticate_user(db, "nonexistentuser", "test1234!")
    assert wrong_password_user is False

def test_create_access_token(test_user):
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)
    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                                 options={"verify_signature": False})
    assert decoded_payload["sub"] == username
    assert decoded_payload["id"] == user_id
    assert decoded_payload["role"] == role

@pytest.mark.asyncio
async def test_get_current_user():
    encode = {"sub": 'testuser', "id": 1, "role": 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"