def test_list_tags_empty(client, auth_headers):
    response = client.get("/tags", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_tags_are_deduplicated_across_bookmarks(client, auth_headers):
    client.post("/bookmarks", json={"url": "https://a.com", "tags": ["tech"]}, headers=auth_headers)
    client.post("/bookmarks", json={"url": "https://b.com", "tags": ["tech", "news"]}, headers=auth_headers)

    response = client.get("/tags", headers=auth_headers)
    assert response.status_code == 200
    assert sorted(t["name"] for t in response.json()) == ["news", "tech"]
