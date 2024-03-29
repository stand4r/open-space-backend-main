from random import randint
from fastapi import APIRouter, HTTPException
from config.config import GMAIL_EMAIL, GMAIL_PASSWORD
from db.RedisDB import redisdb
from models.UserModel import User
from db.PostgreDB import db_users
from passlib.hash import bcrypt
from mail.MailApi import mail
import secrets

authRouter = APIRouter(
    prefix="/auth",
    tags=['auth'],
)


def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)

def eq_passwd(password: str, hash: str) -> str:
    return bcrypt.verify(password, hash)

def gen_randkey() -> str:
    return secrets.token_hex(16)

@authRouter.post("/login")
def login(username:str, password:str) -> dict:
    if not db_users.is_user(username=username):
        raise HTTPException(404, f"Not found user {username}")
    user = db_users.find_by_username(username) # User object from database
    if user == None:
        raise HTTPException(405, f"Bad load user {username}")
    if eq_passwd(password, user[5]):
        return {"status": "OK"}
    else:
        raise HTTPException(403, f"Incorrect password")


@authRouter.post("/confirm")
def confirm(rayid:str, code:int) -> str:
    try:
        row = redisdb.getConfirmRay(rayid)
        if code == int(row["conf_code"]):
            if not db_users.change_user(row["username"], "email_confirmed", True):
                raise HTTPException(401, "Error in db_users.change_user")
            redisdb.removeConfirmRay(rayid)
            return "OK"
        else: 
            raise HTTPException(401, "Incorrect code")
    except Exception as e:
        print(f'[authRouter] Confirm code error: {e}')
        raise HTTPException(401, "Incorrect code")


@authRouter.post("/register")
def register(username:str, password:str, email:str, first_name:str, last_name:str) -> dict:
    if password == "":
        raise HTTPException(401, "Register error")
    if db_users.is_user(username):
        raise HTTPException(400, "Username already uses")
    try:
        user = User(username=username, password_hash=get_password_hash(password), email=email, email_confirmed=False, profile={"first_name": first_name, "last_name": last_name, "status": "", "profile_picture": ""}, projects=list(), integrations=list())
        if not db_users.create_user(user.dict()):
            raise HTTPException(401, "Error in db_users.create_users()")
        ray_id = gen_randkey()
        conf_code = randint(1000,9999)
        mail.sendTemplate(code=conf_code, to_addr=email)
        redisdb.addConfirmRay(rayid=ray_id, code=conf_code, username=username)
        return {"ray_id": ray_id}
    except Exception as ex:
        raise HTTPException(401, "Register error")
