from fastapi import status
def test_app_health(client):
    res = client.get('/health/')
    assert res.status_code == status.HTTP_200_OK