from fastapi import status
from app import schemas
from app.config import settings
import jwt
import pytest

users_route = '/users/'
auth_route = '/login/'

# Test root directory is accessible
def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == "Hello World"
    assert res.status_code == status.HTTP_200_OK

# Test creating a single user
def test_create_user(client, test_user):
    user_data = {'email': 'testemail@gmail.com', 'password': 'password123@'}
    res = client.post(users_route, json=user_data)
    assert res.status_code == status.HTTP_201_CREATED

# Test Login User
def test_successful_login_user(client, test_user):
    user_data = {'username': test_user.get('email'), 'password': test_user.get('password')}
    res = client.post(auth_route, data=user_data)
    login_res = res.json()
    payload = jwt.decode(login_res.get('access_token'), key=settings.secret_key, algorithms=[settings.algorithm])
    assert res.status_code == status.HTTP_202_ACCEPTED
    assert login_res.get('token_type') == "bearer"
    assert payload.get("user_id") == test_user.get('email')

# Using parametrization to test multiple test cases
@pytest.mark.parametrize("username, password, status_code", [
    ("wrongemail@gmail.com", "password123@", 403),
    ("dummyemail1@gmail.com", "wrongpassword", 403),
    ("wrongemail@gmail.com", "wrongpassword", 403),
    (None, "password123@", 422),
    ("dummyemail1@gmail.com", None, 422)
])
def test_unsuccessful_login_user(client, username, password, status_code):
    user_data = {'username': username, 'password': password}
    res = client.post(auth_route, data=user_data)
    assert res.status_code == status_code