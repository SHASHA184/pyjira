from fastapi import FastAPI
import uvicorn
from routers import users, tasks

app = FastAPI()
app.include_router(users.router)
app.include_router(tasks.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
