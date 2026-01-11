# Test Auth Route
from fastapi import status
from app.oauth2 import verify_access_token
from app.models import Attempts
from datetime import datetime, timedelta, timezone
import pytest

auth_route = '/login/'
def test_basic_correct_login(client, test_user):
    user_data = {'username': test_user.get('email'), 'password': test_user.get('password')}
    res = client.post(auth_route, data=user_data)
    token = res.json().get('access_token')
    tokenData = verify_access_token(token)
    assert res.status_code == status.HTTP_202_ACCEPTED
    assert tokenData.email == test_user.get('email')

def test_basic_incorrect_login(client, test_user):
    user_data = {'username': test_user.get('email'), 'password': 'wrong password'}
    res = client.post(auth_route, data=user_data)
    assert res.status_code == status.HTTP_403_FORBIDDEN

def test_non_existent_user(client, test_user):
    user_data = {'username': 'dne@gmail.com', 'password': test_user.get('password')}
    res = client.post(auth_route, data=user_data)
    assert res.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.parametrize("password, expected_status_code", [
    ('wrong_password', status.HTTP_403_FORBIDDEN),
    ('wrong_password', status.HTTP_403_FORBIDDEN),
    ('wrong_password', status.HTTP_403_FORBIDDEN),
    ('wrong_password', status.HTTP_403_FORBIDDEN),
    ('wrong_password', status.HTTP_403_FORBIDDEN),
    ('correct_password', status.HTTP_202_ACCEPTED)
])
def test_max_login_attempts(client, test_user, password, expected_status_code):
    user_data = {'username': test_user.get('email'), 'password': test_user.get('password') if password == 'correct_password' else password}
    res = client.post(auth_route, data=user_data)
    assert res.status_code == expected_status_code

def test_too_many_attempts(client, test_user):
    user_data = {"username": test_user["email"], "password": "wrong_password"}
    for _ in range(5): # 403 for first max_login_attempts
        res = client.post(auth_route, data=user_data)
        assert res.status_code == status.HTTP_403_FORBIDDEN
    res = client.post(auth_route, data=user_data)# Locked, 429
    assert res.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_correct_attempt_during_cooldown(client, test_user):
    bad = {"username": test_user["email"], "password": "wrong_password"}
    for _ in range(6):
        client.post(auth_route, data=bad)
    good = {"username": test_user["email"], "password": test_user["password"]}
    res = client.post(auth_route, data=good)
    assert res.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_correct_attempt_after_cooldown(client, session, test_user):
    u_id = test_user.get('email')
    attempt = Attempts(user_id=u_id, attempts=10, cooldown=datetime.now(timezone.utc) - timedelta(seconds=1))
    session.add(attempt)
    session.commit()
    user_data = {'username': test_user.get('email'), 'password': test_user.get('password')}
    res = client.post(auth_route, data=user_data)
    assert res.status_code == status.HTTP_202_ACCEPTED

def test_incorrect_attempt_after_cooldown(client, session, test_user):
    u_id = test_user.get('email')
    attempt = Attempts(user_id=u_id, attempts=10, cooldown=datetime.now(timezone.utc) - timedelta(seconds=1))
    session.add(attempt)
    session.commit()
    user_data = {'username': test_user.get('email'), 'password': 'wrong password'}
    res = client.post(auth_route, data=user_data)
    assert res.status_code == status.HTTP_403_FORBIDDEN

# Prevent data leak from incorrect attempts by treating accts that don't exist as if they do
def test_too_many_attempts_non_existant_user(client, test_user):
    bad = {"username": "dneexist@yahoo.com", "password": test_user.get('password')}
    for _ in range(5):
        res = client.post(auth_route, data=bad)
        assert res.status_code == status.HTTP_403_FORBIDDEN
    still_bad = {"username": "dneexist@yahoo.com", "password": test_user.get('password')}
    res = client.post(auth_route, data=still_bad)
    assert res.status_code == status.HTTP_429_TOO_MANY_REQUESTS