from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import json
import os
import uvicorn

app = FastAPI()

# To-Do 항목 모델
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# JSON 파일 경로
TODO_FILE = "todo.json"

# JSON 파일에서 To-Do 항목 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# JSON 파일에 To-Do 항목 저장
def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4)

# To-Do 목록 조회
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# 신규 To-Do 항목 추가
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

# To-Do 항목 수정
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos[i] = updated_todo.dict()
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found!!!_SJ")

# To-Do 항목 삭제
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    original_length = len(todos)
    todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(todos) < original_length:
        save_todos(todos)
        return {"message": "To-Do item deleted"}
    raise HTTPException(status_code=404, detail="To-Do item not found to delete")


# (A) API용: 완료 처리 후 JSON 반환
@app.post("/todos/{todo_id}/finish", response_model=TodoItem)
def finish_todo_api(todo_id: int):
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            if not t.get("completed", False):
                t["completed"] = True
                save_todos(todos)
            return t  # 이미 true여도 그대로 반환
    raise HTTPException(status_code=404, detail="To-Do item not found")

# (B) 페이지용: 버튼 누르면 완료 처리 → 루트로 리다이렉트
@app.post("/finish/{todo_id}")
def finish_todo_redirect(todo_id: int):
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            if not t.get("completed", False):
                t["completed"] = True
                save_todos(todos)
            return RedirectResponse(url="/", status_code=303)
    raise HTTPException(status_code=404, detail="To-Do item not found")

# HTML 파일 서빙
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# 자동 배포 테스트 성공기원 1순위

