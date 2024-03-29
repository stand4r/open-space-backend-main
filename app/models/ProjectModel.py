from pydantic import BaseModel

class Project(BaseModel):
    name:str
    user_admin:int
    type: str
    link:str
    status:str
    about:str
    public: bool