def test_requires_api_key(client):
    response = client.get("/bookmarks")
    assert response.status_code == 401


def test_rejects_wrong_api_key(client):
    response = client.get("/bookmarks", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_create_and_get_bookmark(client, auth_headers):
    response = client.post(
        "/bookmarks",
        json={"url": "https://example.com", "tags": ["reading", "tech"]},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://example.com"
    assert body["title"] is None
    assert sorted(body["tags"]) == ["reading", "tech"]

    get_response = client.get(f"/bookmarks/{body['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json() == body


def test_get_nonexistent_bookmark_404(client, auth_headers):
    response = client.get("/bookmarks/999", headers=auth_headers)
    assert response.status_code == 404


def test_list_filters_by_tag(client, auth_headers):
    client.post("/bookmarks", json={"url": "https://a.com", "tags": ["tech"]}, headers=auth_headers)
    client.post("/bookmarks", json={"url": "https://b.com", "tags": ["cooking"]}, headers=auth_headers)

    response = client.get("/bookmarks?tag=tech", headers=auth_headers)
    assert response.status_code == 200
    assert [b["url"] for b in response.json()] == ["https://a.com"]


def test_list_searches_title_and_url(client, auth_headers):
    created = client.post("/bookmarks", json={"url": "https://python.org"}, headers=auth_headers).json()
    client.patch(f"/bookmarks/{created['id']}", json={"title": "Python homepage"}, headers=auth_headers)
    client.post("/bookmarks", json={"url": "https://other.com"}, headers=auth_headers)

    response = client.get("/bookmarks?q=python", headers=auth_headers)
    assert [b["url"] for b in response.json()] == ["https://python.org"]


def test_update_bookmark_title_and_tags(client, auth_headers):
    created = client.post(
        "/bookmarks", json={"url": "https://example.com", "tags": ["a"]}, headers=auth_headers
    ).json()

    response = client.patch(
        f"/bookmarks/{created['id']}",
        json={"title": "New title", "tags": ["b", "c"]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New title"
    assert sorted(body["tags"]) == ["b", "c"]


def test_update_nonexistent_bookmark_404(client, auth_headers):
    response = client.patch("/bookmarks/999", json={"title": "x"}, headers=auth_headers)
    assert response.status_code == 404


def test_delete_bookmark(client, auth_headers):
    created = client.post("/bookmarks", json={"url": "https://example.com"}, headers=auth_headers).json()

    delete_response = client.delete(f"/bookmarks/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/bookmarks/{created['id']}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_nonexistent_bookmark_404(client, auth_headers):
    response = client.delete("/bookmarks/999", headers=auth_headers)
    assert response.status_code == 404
