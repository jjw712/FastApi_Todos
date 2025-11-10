from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import json
import os
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Prometheus ∏ﬁ∆Æ∏ØΩ∫ ø£µÂ∆˜¿Œ∆Æ (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
# To-Do ?ï≠Î™? Î™®Îç∏
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# JSON ?åå?ùº Í≤ΩÎ°ú
TODO_FILE = "todo.json"

# JSON ?åå?ùº?óê?Ñú To-Do ?ï≠Î™? Î°úÎìú
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

# JSON ?åå?ùº?óê To-Do ?ï≠Î™? ????û•
def save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4)

# To-Do Î™©Î°ù Ï°∞Ìöå
@app.get("/todos", response_model=list[TodoItem])
def get_todos():
    return load_todos()

# ?ã†Í∑? To-Do ?ï≠Î™? Ï∂îÍ??
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo

# To-Do ?ï≠Î™? ?àò?†ï
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos[i] = updated_todo.dict()
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found!!!_SJ")

# To-Do ?ï≠Î™? ?Ç≠?†ú
@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    original_length = len(todos)
    todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(todos) < original_length:
        save_todos(todos)
        return {"message": "To-Do item deleted"}
    raise HTTPException(status_code=404, detail="To-Do item not found to delete")


# (A) API?ö©: ?ôÑÎ£? Ï≤òÎ¶¨ ?õÑ JSON Î∞òÌôò
@app.post("/todos/{todo_id}/finish", response_model=TodoItem)
def finish_todo_api(todo_id: int):
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            if not t.get("completed", False):
                t["completed"] = True
                save_todos(todos)
            return t  # ?ù¥ÎØ? true?ó¨?èÑ Í∑∏Î??Î°? Î∞òÌôò
    raise HTTPException(status_code=404, detail="To-Do item not found")

# (B) ?éò?ù¥Ïß??ö©: Î≤ÑÌäº ?àÑÎ•¥Î©¥ ?ôÑÎ£? Ï≤òÎ¶¨ ?Üí Î£®Ìä∏Î°? Î¶¨Îã§?ù¥?†â?ä∏
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

# HTML ?åå?ùº ?ÑúÎπ?
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as file:
        content = file.read()
    return HTMLResponse(content=content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

# ?ûê?èô Î∞∞Ìè¨ ?Öå?ä§?ä∏ ?Ñ±Í≥µÍ∏∞?õê 1?àú?úÑ

