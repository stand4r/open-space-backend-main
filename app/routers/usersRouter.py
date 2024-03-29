from db.PostgreDB import db_users
from passlib.context import CryptContext
from typing import List, Dict, Union
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

usersRouter = APIRouter(
    prefix="/users",
    tags=['users'],
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

class Project(BaseModel):
    username: str

class ProjectLink(BaseModel):
    username: str
    link: str

class ProjectsResponse(BaseModel):
    status: str
    projects: List[Project] = []

class UserIDResponse(BaseModel):
    status: str
    id: int

class StatusResponse(BaseModel):
    status: str

class UsernameModel(BaseModel):
    username: str = Field(...)

class ChangeUserModel(BaseModel):
    username: str = Field(...)
    key: str = Field(...)
    value: str = Field(...)

class CreateUserModel(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)

class User(BaseModel):
    username: str
    email: str

class UsersResponse(BaseModel):
    status: str
    users: Union[List[User], str]


def error_handler(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
    return inner

@error_handler
@usersRouter.get("/users", response_model=UsersResponse)
def get_all_users() -> UsersResponse:
    users = db_users.get_all_users()
    return UsersResponse(status="OK", users=users)

@error_handler
@usersRouter.post("/is_user", response_model=UsersResponse)
def is_user(username: UsernameModel) -> Dict[str, str]:
    user_status = "used" if db_users.is_user(username=username.username) else "not used"
    return {"status": "OK", "username": user_status}

@error_handler
@usersRouter.post("/find_by_username", response_model=UsersResponse)
def find_by_username(username: UsernameModel) -> Dict[str, str]:
    user_info = db_users.find_by_username(username=username.username)
    return {"status": "OK", "username": user_info}

@error_handler
@usersRouter.post("/change_user", response_model=StatusResponse)
def change_user(user_changes: ChangeUserModel) -> Dict[str, str]:
    if db_users.change_user(username=user_changes.username, key=user_changes.key, value=user_changes.value):
        return {"status": "OK"}
    else:
        return {"status": "FAILED", "reason": "User update failed."}

@error_handler
@usersRouter.post("/create_user", response_model=StatusResponse)
def register(user_data: CreateUserModel) -> Dict[str, str]:
    user_data.password = get_password_hash(user_data.password)
    if db_users.create_user(user_data.dict()):
        return {"status": "OK"}
    return {"status": "BAD", "reason": "User creation failed."}

@error_handler
@usersRouter.post("/get_all_projects", response_model=ProjectsResponse)
def get_all_projects(username: str):
    projects = db_users.get_all_projects(username=username)
    return {"status": "OK", "projects": projects}

@error_handler
@usersRouter.get("/get_id_by_username", response_model=UserIDResponse)
def get_id_by_username(username: str):
    user_id = db_users.get_id_by_username(username=username)
    return {"status": "OK", "id": user_id}

@error_handler
@usersRouter.post("/add_project", response_model=StatusResponse)
def add_project(project_details: ProjectLink):
    success = db_users.add_project(username=project_details.username, link=project_details.link)
    if not success:
        return {"status": "BAD"}
    return {"status": "OK"}
