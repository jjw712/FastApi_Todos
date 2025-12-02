from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import json
import os
import uvicorn
import logging
import time
from queue import Queue
from os import getenv
from fastapi import Request
from prometheus_fastapi_instrumentator import Instrumentator
from logging_loki import LokiSHandler


app = FastAPI()

# Prometheus ��Ʈ���� ��������Ʈ (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
# To-Do ?���? 모델

# === Loki ENV 체크 ===
LOKI_ENDPOINT = getenv("LOKI_ENDPOINT")
assert LOKI_ENDPOINT, "LOKI_ENDPOINT not set"

loki_handler = LokiHandler(
    url=LOKI_ENDPOINT,
    tags={"application": "fastapi"},
    version="1",
)

# loki_logs_handler = LokiQueueHandler(
#     Queue(-1),
#     url=getenv("LOKI_ENDPOINT"),
#     tags={"application": "fastapi"},
#     version="1",
# )


# Custom access logger (ignore Uvicorn's default logging)
custom_logger = logging.getLogger("custom.access")
custom_logger.setLevel(logging.INFO)

# Add Loki handler (assuming `loki_logs_handler` is correctly configured)
custom_logger.addHandler(loki_handler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time  # Compute response time

    log_message = (
        f'{request.client.host} - "{request.method} {request.url.path} HTTP/1.1" {response.status_code} {duration:.3f}s'
    )

    # **Only log if duration exists**
    if duration:
        custom_logger.info(log_message)

    return response

class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# JSON ?��?�� 경로
TODO_FILE = "todo.json"

# JSON ?��?��?��?�� To-Do ?���? 로드
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# JSON ?��?��?�� To-Do ?���? ????��
def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4)

# To-Do 목록 조회
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# ?���? To-Do ?���? 추�??
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

# To-Do ?���? ?��?��
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos[i] = updated_todo.dict()
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found!!!_SJ")

# To-Do ?���? ?��?��
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    original_length = len(todos)
    todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(todos) < original_length:
        save_todos(todos)
        return {"message": "To-Do item deleted"}
    raise HTTPException(status_code=404, detail="To-Do item not found to delete")


# (A) API?��: ?���? 처리 ?�� JSON 반환
@app.post("/todos/{todo_id}/finish", response_model=TodoItem)
def finish_todo_api(todo_id: int):
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            if not t.get("completed", False):
                t["completed"] = True
                save_todos(todos)
            return t  # ?���? true?��?�� 그�??�? 반환
    raise HTTPException(status_code=404, detail="To-Do item not found")

# (B) ?��?���??��: 버튼 ?��르면 ?���? 처리 ?�� 루트�? 리다?��?��?��
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

# HTML ?��?�� ?���?
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# ?��?�� 배포 ?��?��?�� ?��공기?�� 1?��?��

