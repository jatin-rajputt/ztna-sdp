def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}