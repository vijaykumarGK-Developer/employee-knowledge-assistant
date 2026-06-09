import io

from fastapi.testclient import TestClient


def test_upload_as_employee(client: TestClient, user_headers: dict):
    res = client.post("/api/documents/upload", data={
        "title": "Test", "department": "all",
    }, files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}, headers=user_headers)
    assert res.status_code == 403


def test_upload_as_admin(client: TestClient, admin_headers: dict):
    res = client.post("/api/documents/upload", data={
        "title": "Admin Doc", "department": "all",
    }, files={"file": ("test.txt", io.BytesIO(b"hello world"), "text/plain")}, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Admin Doc"
    assert data["file_type"] == "txt"


def test_upload_invalid_type(client: TestClient, admin_headers: dict):
    res = client.post("/api/documents/upload", data={
        "title": "Bad", "department": "all",
    }, files={"file": ("test.exe", io.BytesIO(b"data"), "application/octet-stream")}, headers=admin_headers)
    assert res.status_code == 400


def test_list_documents(client: TestClient, admin_headers: dict, sample_doc: str):
    res = client.get("/api/documents/", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(d["id"] == sample_doc for d in data["items"])


def test_get_document(client: TestClient, admin_headers: dict, sample_doc: str):
    res = client.get(f"/api/documents/{sample_doc}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["id"] == sample_doc


def test_get_document_not_found(client: TestClient, admin_headers: dict):
    res = client.get("/api/dockets/nonexistent-id", headers=admin_headers)
    assert res.status_code == 404


def test_delete_document(client: TestClient, admin_headers: dict, sample_doc: str):
    res = client.delete(f"/api/documents/{sample_doc}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "deleted"

    res = client.get(f"/api/documents/{sample_doc}", headers=admin_headers)
    assert res.status_code == 404


def test_delete_as_employee(client: TestClient, user_headers: dict, sample_doc: str):
    res = client.delete(f"/api/documents/{sample_doc}", headers=user_headers)
    assert res.status_code == 403
