from fastapi import FastAPI
from routers import users,tickets
app = FastAPI()

app.include_router(users.router)
app.include_router(tickets.router)