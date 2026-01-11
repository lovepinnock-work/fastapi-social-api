from fastapi import status
from sqlalchemy import select
from app import models
import pytest

@pytest.fixture
def test_vote(test_posts, test_user, session):
    post_to_vote_for = test_posts[1]
    vote = models.Vote(user_id=test_user.get("id"), 
                post_id=post_to_vote_for.id)
    session.add(vote)
    session.commit()
    return post_to_vote_for

def test_vote_once_on_post(authorized_client, test_posts):
    vote_data = {"post_id": test_posts[0].id, "vote_dir": 1}
    res = authorized_client.post("/vote/", json=vote_data)
    assert res.status_code == status.HTTP_201_CREATED

def test_vote_twice_post(authorized_client, test_posts, test_vote):
    vote_data = {"post_id": test_vote.id, "vote_dir": 1}
    res = authorized_client.post("/vote/", json=vote_data)
    assert res.status_code == status.HTTP_409_CONFLICT

def test_unvote(authorized_client, test_posts, test_vote):
    vote_data = {"post_id": test_vote.id, "vote_dir": 0}
    res = authorized_client.post("/vote/", json=vote_data)
    assert res.status_code == status.HTTP_201_CREATED

def test_unvote_on_post_not_voted_on(authorized_client, test_posts):
    vote_data = {"post_id": test_posts[0].id, "vote_dir": 0}
    res = authorized_client.post("/vote/", json=vote_data)
    assert res.status_code == status.HTTP_404_NOT_FOUND

def test_vote_on_non_existant_post(authorized_client):
    vote_data = {"post_id": 10000, "vote_dir": 1}
    res = authorized_client.post("/vote/", json=vote_data)
    assert res.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_vote(client, test_vote):
    vote_data = {"post_id": test_vote.id, "vote_dir": 0}
    res = client.post("/vote/", json=vote_data)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
