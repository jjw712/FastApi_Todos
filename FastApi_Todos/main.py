from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import os
import uvicorn

app = FastAPI()

# To-Do �׸� ��
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# JSON ���� ���
TODO_FILE = "todo.json"

# JSON ���Ͽ��� To-Do �׸� �ε�
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# JSON ���Ͽ� To-Do �׸� ����
def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4)

# To-Do ��� ��ȸ
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# �ű� To-Do �׸� �߰�
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

# To-Do �׸� ����
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos[i] = updated_todo.dict()
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found!!!_SJ")

# To-Do �׸� ����
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    original_length = len(todos)
    todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(todos) < original_length:
        save_todos(todos)
        return {"message": "To-Do item deleted"}
    raise HTTPException(status_code=404, detail="To-Do item not found to delete")

# HTML ���� ����
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# �ڵ� ���� �׽�Ʈ ������� 1����
