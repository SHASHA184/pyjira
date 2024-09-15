from fastapi import FastAPI
import uvicorn
from routers import users, tasks, auth

app = FastAPI()
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(auth.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
