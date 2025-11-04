import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 
    save_todos([])
    yield
    #
    save_todos([])

def test_root_serves_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "To-Do List" in r.text


def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"

def test_create_todo():
    todo = {"id": 1, "title": "Test", "description": "Test description", "completed": False}
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Test"

def test_create_todo_invalid():
    todo = {"id": 1, "title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    updated_todo = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

def test_update_todo_not_found():
    updated_todo = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 404

def test_delete_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
    
def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 404
    #assert response.json()["message"] == "To-Do item deleted"
    
def test_finish_todo():
    # 준비: 미완료 항목 하나 저장
    todo = TodoItem(id=10, title="FinishMe", description="desc", completed=False)
    save_todos([todo.dict()])  # pydantic v2면 todo.model_dump() 써도 됨

    # 액션: 완료 처리
    r = client.post("/todos/10/finish")
    assert r.status_code in (200, 303)

    # 검증: completed == True
    data = client.get("/todos").json()
    item = next((t for t in data if t["id"] == 10), None)
    assert item and item["completed"] is True
    
def test_finish_not_found():
    r = client.post("/todos/999999/finish")
    assert r.status_code == 404


def test_finish_via_put():
    todo = TodoItem(id=11, title="ToBeFinished", description="desc", completed=False)
    save_todos([todo.dict()])
    r = client.put("/todos/11", json={"id": 11, "title": "ToBeFinished", "description": "desc", "completed": True})
    assert r.status_code == 200
    assert r.json()["completed"] is True

