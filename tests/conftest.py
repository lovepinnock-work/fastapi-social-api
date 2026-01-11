from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi import status
from fastapi.testclient import TestClient
from app import config, models
from app.main import app
from app.database import get_db
from app.oauth2 import create_access_token
import pytest

settings = config.settings

SQLALCHEMY_TEST_DATABASE_URL = f"{settings.database_dialect}+{settings.database_driver}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Multiple fixutres useful in order to access both session and client objects
@pytest.fixture
def session():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)    
    with TestingSessionLocal() as db:
        yield db

@pytest.fixture
def client(session):
    def get_test_db():
        yield session
    # Run before test runs
    app.dependency_overrides[get_db] = get_test_db
    # Yield for our tests
    with TestClient(app=app) as tc:
        yield tc
    # Run after test runs
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client):
    user_data = {'email': 'dummyemail1@gmail.com', 'password': 'password123@'}
    res = client.post('/users/', json=user_data)
    assert res.status_code == status.HTTP_201_CREATED
    new_user = res.json()
    new_user.setdefault('email', user_data.get('email'))
    new_user.setdefault('password', user_data.get('password'))
    return new_user

@pytest.fixture
def test_multiple_users(client):
    user_data = [
        {'email': 'dummyemail2@gmail.com', 'password': 'password123@'},
        {'email': 'dummyemail3@gmail.com', 'password': 'password123@'},
        {'email': 'dummyemail4@gmail.com', 'password': 'password123@'},         
        {'email': 'dummyemail5@gmail.com', 'password': 'password123@'},
    ]
    new_user_data = []
    for ud in user_data:
        res = client.post('/users/', json=ud)
        assert res.status_code == status.HTTP_201_CREATED
        new_user = res.json()
        new_user.setdefault('password', ud.get('password'))
        new_user_data.append(new_user)
    return new_user_data

@pytest.fixture
def token(test_user):
    data = {'user_id': test_user.get('email')}
    access_token = create_access_token(data=data, expires=settings.access_token_expiration_minutes)
    return access_token

@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
def test_posts(test_user, test_multiple_users, session):
    posts = [
        ("Title1", "Content1", test_user.get('id')),
        ("Title2", "Content2", test_user.get('id')),
        ("Title3", "Content3", test_user.get('id')),
        ("Title4", "Content4", test_user.get('id'), False),
        ("Title5", "Content5", test_multiple_users[0].get('id')),
        ("Title6", "Content6", test_multiple_users[0].get('id'), False),           
    ]
    session.add_all(map(lambda d: models.Post(**d),
                         map(lambda p: {'title': p[0], 
                                        'content': p[1], 
                                        'owner_id': p[2],
                                        'published': True if len(p) < 4 else p[3] }
                             ,posts)))
    session.commit()
    return session.scalars(select(models.Post)).all()
    
