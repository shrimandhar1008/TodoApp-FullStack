from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    # assert response.json() is None
    assert response.json()["username"] == "shreecoding"
    assert response.json()["role"] == "admin"
    assert response.json()["email"] == "shrimandhar@email.com"
    assert response.json()["first_name"] == "Shrimandhar"
    assert response.json()["last_name"] == "Magdum"
    assert response.json()["phone_number"] == "751731008"

def test_change_password_change(test_user):
    new_password_data = {
        "password": "test1234!",
        "new_password": "newpassword123"
    }
    response = client.put("/user/password", 
                          json=new_password_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # db = TestingSessionLocal()
    # updated_user = db.query(Users).filter(Users.id == 1).first()
    # assert bcrypt_context.verify("newpassword123", updated_user.hashed_password)

def test_change_password_incorrect_current_password(test_user):
    new_password_data = {
        "password": "wrongpassword",
        "new_password": "newpassword123"
    }
    response = client.put("/user/password", 
                          json=new_password_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Error on password change. Please check your current password and try again."}

def test_change_phone_number_success(test_user):
    new_phone_number = "1234567890"
    response = client.put(f"/user/phone_number/{new_phone_number}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    updated_user = db.query(Users).filter(Users.id == 1).first()
    assert updated_user.phone_number == new_phone_number