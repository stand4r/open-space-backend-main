from fastapi import FastAPI
from routers.authenticationRouter import authRouter
from routers.usersRouter import usersRouter
from routers.projectsRouter import projectsRouter
from routers.projectsFeed import feedRouter

app = FastAPI()

app.include_router(authRouter, prefix="/api")
app.include_router(usersRouter, prefix="/api")
app.include_router(projectsRouter, prefix="/api")
app.include_router(feedRouter, prefix="/api")

