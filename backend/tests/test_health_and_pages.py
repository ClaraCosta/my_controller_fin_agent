def test_login_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "MY CONTROLLER FINANCE" in response.text

