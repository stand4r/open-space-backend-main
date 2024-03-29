from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from db.PostgreDB import db_projects
from models.ProjectModel import Project
from pydantic import BaseModel, Json


projectsRouter = APIRouter(
    prefix="/projects",
    tags=['projects']
)

'''
Projects DB


id: integer
users: jsonb (null)
user_admin: integer
link: text (null)
about: text
name: text
status: text
photo: text
count_users: bigint
params: jsonb (null)
'''

class ProjectCreationData(BaseModel):
    name: str
    user_admin: int
    type: str
    link: str
    status: str
    about: str
    count_users: int
    users: Json

class ResponseModel(BaseModel):
    status: str
    id: Optional[int] = None

class Project(BaseModel):
    name: str

class AdminProjectResponse(BaseModel):
    status: str
    projects: List[Project]

class ProjectName(BaseModel):
    name: str

class ProjectStatus(BaseModel):
    status: str
    name: str

def error_handler(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail="Internal server error.")
    return inner

@error_handler
@projectsRouter.get("/get_id_by_name/{name}", response_model=ResponseModel)
def get_id_by_name(name: str) -> ResponseModel:
    project_id = db_projects.get_id_by_name(name=name)
    if project_id is not None:
        return {"status": "OK", "id": project_id}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

@error_handler
@projectsRouter.post("/create_project", response_model=ResponseModel)
def create_project(project_data: ProjectCreationData) -> ResponseModel:
    if not db_projects.create_project(project_data.dict()):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create the project.")
    return {"status": "OK"}

@error_handler
@projectsRouter.get("/get_all_projects", response_model=AdminProjectResponse)
def get_all_projects() -> dict:
    return {"status": "OK", "projects": db_projects.get_all_projects()}

@error_handler
@projectsRouter.post("/get_projects_by_condition", response_model=AdminProjectResponse)
def get_projects_by_condition(condition: str) -> dict:
    return {"status": "OK", "projects": db_projects.get_projects_by_condition(condition=condition)}

@error_handler
@projectsRouter.get("/get_admin_projects/{user_id}", response_model=AdminProjectResponse)
def get_admin_projects(user_id: str) -> dict:
    return {"status": "OK", "projects": db_projects.get_admin_projects(user_id=user_id)}

@error_handler
@projectsRouter.put("/change_params_project")
def change_params_project(name: str, key: str, value: str) -> dict:
    success = db_projects.change_params_project(name=name, key=key, value=value)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or update failed.")
    return {"status": "OK"}

@error_handler
@projectsRouter.post("/is_project", response_model=ProjectStatus)
def is_project(project_name: ProjectName) -> ProjectStatus:
    project_usage_status = "used" if db_projects.is_project(name=project_name.name) else "not used"
    return {"status": "OK", "name": project_usage_status}