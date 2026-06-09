from fastapi.testclient import TestClient


def test_create_chat(client: TestClient, user_headers: dict):
    res = client.post("/api/chats/", headers=user_headers)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    assert data["title"] == "New Chat"


def test_list_chats(client: TestClient, user_headers: dict):
    client.post("/api/chats/", headers=user_headers)
    res = client.get("/api/chats/", headers=user_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_chat(client: TestClient, user_headers: dict):
    chat = client.post("/api/chats/", headers=user_headers).json()
    res = client.get(f"/api/chats/{chat['id']}", headers=user_headers)
    assert res.status_code == 200
    assert "messages" in res.json()


def test_get_chat_not_found(client: TestClient, user_headers: dict):
    res = client.get("/api/chats/nonexistent", headers=user_headers)
    assert res.status_code == 404


def test_send_message(client: TestClient, user_headers: dict):
    chat = client.post("/api/chats/", headers=user_headers).json()
    res = client.post(f"/api/chats/{chat['id']}/messages", json={
        "content": "What is the leave policy?",
    }, headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["message"]["role"] == "user"
    assert data["answer"]["role"] == "assistant"


def test_submit_feedback(client: TestClient, user_headers: dict):
    chat = client.post("/api/chats/", headers=user_headers).json()
    msg_res = client.post(f"/api/chats/{chat['id']}/messages", json={
        "content": "Hello",
    }, headers=user_headers).json()
    msg_id = msg_res["answer"]["id"]
    res = client.post(f"/api/chats/messages/{msg_id}/feedback", json={
        "feedback": True,
    }, headers=user_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_delete_chat(client: TestClient, user_headers: dict):
    chat = client.post("/api/chats/", headers=user_headers).json()
    res = client.delete(f"/api/chats/{chat['id']}", headers=user_headers)
    assert res.status_code == 200
    res = client.get(f"/api/chats/{chat['id']}", headers=user_headers)
    assert res.status_code == 404
