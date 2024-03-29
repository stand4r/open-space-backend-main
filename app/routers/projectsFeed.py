from fastapi import APIRouter, Depends
from db.RedisDB import redisdb
from db.PostgreDB import db_users, db_projects
from pydantic import BaseModel
from typing import List

class User(BaseModel):
    id: int
    weight: float

class Project(BaseModel):
    id: int
    weight: float
    participants: List[User]

class ProjectRecommendation(BaseModel):
    id: int
    recommendation_score: float


feedRouter = APIRouter(
    prefix="/profile",
    tags=['profile']
)


def generate_recommendations(projects: List[Project]) -> List[ProjectRecommendation]:
    recommendations = []

    for project in projects:
        score = project.weight
        #Здесь будет код 2 уровня
        recommendations.append(ProjectRecommendation(id=project.id, recommendation_score=score))
    
    return sorted(recommendations, key=lambda x: x.recommendation_score, reverse=True)

def get_projects():
    return db_projects.get_all_projects()

@feedRouter.get("/recommendations/", response_model=List[ProjectRecommendation])
def get_recommendations(user_id: int, projects: List[Project] = Depends(get_projects)):
    return generate_recommendations(projects, user_id)




'''@feedRouter.post("/get_projects_feed")
def get_projects_feed(session_key: str):
    try:
        id = redisdb.getSession(session_key)
        projects = db_projects.get_all_projects()
        return {"status": "OK", "projects": getRatingFeed(id, projects)}
    except:
        raise HTTPException(status_code=500, detail="Internal server error.")


class getRatingFeed():
    def __init__(self, id: int, projects: list):
        self._projects = projects
        self.set_feed(id)

    def get_projects(self, id: int):
        projects = []
        if self._projects == None:
            return None
        for project in self._projects:
            diction = {}
            diction["name"] = project["name"]
            diction["type"] = project["type"]
            diction["link"] = project["link"]
            diction["status"] = project["status"]
            diction["about"] = project["about"]
            diction["count"] = projects["users"].keys().count()
            if int(project["user_admin"]) == id:
                diction["role"] = "admin"
            else:
                if str(id) in project["users"].keys() or id in project["users"].keys():
                    diction["role"] = project["users"][str(id)]
                else:
                    diction.clear()
                    continue
            projects.append(diction)
        return projects

    def set_feed(self, id: int):
        projects = self.get_projects(id)
        if projects == None:
            return None
        projects_filter = []

        #здесь будет рекомендательная система

        return projects_filter
'''
