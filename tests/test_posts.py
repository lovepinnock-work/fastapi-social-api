from fastapi import status
from app import schemas
import pytest

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    assert len(res.json()) == len(test_posts)
    assert res.status_code == status.HTTP_200_OK

def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get('/posts/')
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_nonexistent_post(authorized_client, test_posts):
    res = authorized_client.get("f/posts/100000")
    assert res.status_code == status.HTTP_404_NOT_FOUND

def test_existing_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/1")
    post = schemas.PostOut(**res.json())
    assert post.post.title == test_posts[0].title
    assert post.post.content == test_posts[0].content

@pytest.mark.parametrize("title, content, published", [
    ("Title1", "Content1", True),
    ("Title2", "Content2", True),
    ("Title3", "Content3", False)
])
def test_create_post(authorized_client, test_user, title, content, published):
    post_data = dict(title=title, content=content, published=published)
    res = authorized_client.post('/posts/', json=post_data)
    post = schemas.Post(**res.json())
    assert res.status_code == status.HTTP_201_CREATED
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.owner_id == test_user.get('id')

def test_create_post_default_published(authorized_client, test_user):
    post_data = dict(title='testtitle', content='testcontent')
    res = authorized_client.post('/posts/', json=post_data)
    post = schemas.Post(**res.json())
    assert res.status_code == status.HTTP_201_CREATED
    assert post.title == post_data.get('title')
    assert post.content == post_data.get('content')
    assert post.published == True
    assert post.owner_id == test_user.get('id')

def test_unauthorized_user_cant_create_post(client, test_user):
    post_data = dict(title='testtitle', content='testcontent')
    res = client.post('/posts/', json=post_data)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_unauthorized_user_cant_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_authorized_user_can_delete(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert test_posts[0].owner_id == test_user["id"]
    assert res.status_code == status.HTTP_204_NO_CONTENT

def test_user_cant_delete_another_users_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{len(test_posts) - 1}")
    assert res.status_code == status.HTTP_403_FORBIDDEN

def test_user_cant_delete_another_users_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[-1].id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN

def test_unauthorized_update(client, test_posts):
    data = {"title": "UpdatedTitle", "content": "UpdatedContent"}
    res = client.put(f"/posts/{test_posts[0].id}", json=data)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_authorized_update(authorized_client, test_posts):
    data = {
        'title': 'UpdatedTitle', 
        'content': 'UpdatedContent', 
        'id': test_posts[0].id
        }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == status.HTTP_200_OK
    assert updated_post.owner_id == test_posts[0].owner_id

def test_update_non_existent_post(authorized_client, test_posts):
    data = {
        'title': 'UpdatedTitle', 
        'content': 'UpdatedContent', 
        'id': test_posts[0].id
        }
    res = authorized_client.put(f"/posts/{320823094}", json=data)
    assert res.status_code == status.HTTP_404_NOT_FOUND


