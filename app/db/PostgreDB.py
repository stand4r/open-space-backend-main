from config.config import (DBNAME_USERS, DBNAME_PROJECTS, USER, PASSWORD, HOST, PORT)
from psycopg2 import connect
from psycopg2.extras import Json
from typing import Any, Union, Optional
from loguru import logger
import functools
import sys


logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")


def handle_db_errors_bool(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return False
    return wrapper

def handle_db_errors_none(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return None 
    return wrapper


class PostgreDbUsers(object):
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str) -> None:
        try:
            self._db = connect(dbname=dbname, user=user, password=password, host=host, port=port)
            self._db.autocommit = True
            self._cursor = self._db.cursor()
            self.info()
        except Exception as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")

    def __del__(self):
        if hasattr(self, "_cursor"):
            self._cursor.close()
        if hasattr(self, "_db"):
            self._db.close()

    def info(self):
        try:
            self._cursor.execute("SELECT version();")
            record = self._cursor.fetchone()
            self._db.close()
            logger.info("Информация о сервере PostgreSQL \nВы подключены к - ", record)
        except Exception as e:
            logger.error(f"Ошибка [info][users]: {e}")

    @handle_db_errors_bool
    def create_user(self, user: dict) -> bool:
        self._cursor.execute("INSERT INTO users (username, email, integrations, projects, email_confirmed, password_hash, profile) VALUES (%s, %s, %s, %s, %s, %s, %s);", 
                    (user["username"], user["email"],
                    user["integrations"], user["projects"], user["email_confirmed"],
                    user["password_hash"], Json(user["profile"]),))
        self._db.close()
        return True

    @handle_db_errors_bool
    def is_user(self, username: str) -> bool:
        self._cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        if self._cursor.rowcount == 0:
            return False
        self._db.close()
        return True

    @handle_db_errors_bool
    def add_project(self, username: str, link: str) -> bool:
        projects = self.find_by_username(username=username)[7]
        if projects == None:
            projects = [link]
        else:
            projects.append(link)
        if not self.change_user(username=username, key="projects", value=projects):
            return False
        return True

    @handle_db_errors_none
    def get_all_users(self) -> Union[list, None]:
        res = self._execute(f'SELECT * FROM users;', None, "fetch_all")
        self._db.close()
        return res

    @handle_db_errors_none
    def find_by_username(self, username: str) -> Union[tuple, None]:
        self._cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        res = self._cursor.fetchone()
        self._db.close()
        return res

    @handle_db_errors_bool
    def change_user(self, username: str, key: str, value: Any) -> bool:
        self._cursor.execute(f"UPDATE users SET {key} = %s WHERE username = %s;", (value, username))
        self._db.close()
        return True

    @handle_db_errors_none
    def get_all_projects(self, username: str) -> Union[list[tuple], None]:
        if not self.is_user(username=username):
            return None
        res = self._execute("SELECT projects FROM users WHERE username = '%s'", (username,), "fetch_all")
        self._db.close()
        return res

    @handle_db_errors_none
    def get_id_by_username(self, username: str) -> Union[int, None]:
        self._cursor.execute(f"SELECT id FROM users WHERE username = '{username}';")
        res = self._cursor.fetchone()[0]
        self._db.close()
        return res


    @handle_db_errors_bool
    def _execute_bool(self, command: str) -> bool:
        if not command:
            return False
        self._cursor.execute(command)
        return True

    @handle_db_errors_none
    def _execute(self, command: str, values: Optional[tuple] = None, ret: str = "") -> Any:
        if not command:
            return None
        self._cursor.execute(command, values or ())
        
        res = None
        if ret == "fetch_all":
            res = self._cursor.fetchall()
        elif ret == "fetch_one":
            res = self._cursor.fetchone()
        elif ret == "count":
            res = self._cursor.rowcount
        
        return res


class PostgreDbProjects:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str) -> None:
        try:
            self._db = connect(dbname=dbname, user=user, password=password, host=host, port=port)
            self._db.autocommit = True
            self._cursor = self._db.cursor()
            self.info()
        except Exception as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")

    def __del__(self):
        if hasattr(self, "_cursor"):
            self._cursor.close()
        if hasattr(self, "_db"):
            self._db.close()

    def info(self):
        try:
            self._cursor.execute("SELECT version();")
            record = self._cursor.fetchone()
            logger.info("Информация о сервере PostgreSQL \nВы подключены к - ", record)
        except Exception as e:
            logger.error(f"Ошибка [info][projects]: {e}")

    @handle_db_errors_none
    def get_all_projects(self) -> Union[list[tuple], None]:
        self._cursor.execute("SELECT * FROM projects;")
        return self._cursor.fetchall()

    @handle_db_errors_bool
    def create_project(self, project: dict) -> bool:
        if self.is_project(name=project["name"]):
            return False
        params = (project["name"], project["user_admin"], project["type"], project["link"], project["status"], project["about"], project["public"])
        self._cursor.execute("INSERT INTO projects (name, user_admin, type, link, status, about, public) VALUES (%s, %s, %s, %s, %s, %s, %s);", params)
        return True

    @handle_db_errors_none
    def get_projects_by_condition(self, condition: str) -> Union[tuple[Any, ...], None]:
        self._cursor.execute(f"SELECT * FROM projects WHERE {condition}")
        res = self._cursor.fetchall()
        self._db.close()
        return res

    @handle_db_errors_none
    def get_admin_projects(self, user_id: str) -> Union[tuple[Any, ...], None]:
        self._cursor.execute("SELECT * FROM projects WHERE user_admin = %s", (user_id))
        res = self._cursor.fetchall()
        self._db.close()
        return res

    @handle_db_errors_none
    def get_id_by_name(self, name: str) -> Union[int, None]:
        if not self.is_project(name=name):
            return None
        self._cursor.execute(f"SELECT id FROM projects WHERE name = '{name}';")
        res = self._cursor.fetchone()[0]
        self._db.close()
        return res

    @handle_db_errors_bool
    def is_project(self, name: str) -> bool:
        self._cursor.execute("SELECT * FROM projects WHERE name = %s;", (name,))
        if self._cursor.rowcount == 0:
            return False
        self._db.close()
        return True

    @handle_db_errors_bool
    def change_params_project(self, name: str, key: str, value: str) -> bool:
        self._cursor.execute(f"UPDATE projects SET {key} = %s WHERE name = %s;", (value, name))
        self._db.close()
        return True

    @handle_db_errors_bool
    def _execute_bool(self, command: str) -> bool:
        if command == "":
            return False
        self._cursor.execute(command)
        self._db.close()
        return True

    @handle_db_errors_none
    def _execute(self, command: str, ret: str) -> Union[Any, None]:
        if command == "":
            return None
        self._cursor.execute(command)
        if ret == "fetch_all":
            res = self._cursor.fetchall()
        elif ret == "fetch_one":
            res = self._cursor.fetchone()
        elif ret == "count":
            res = self._cursor.rowcount
        self._db.close()
        return res



db_users = PostgreDbUsers(dbname=DBNAME_USERS, user=USER, password=PASSWORD, host=HOST, port=PORT)
db_projects = PostgreDbProjects(dbname=DBNAME_PROJECTS, user=USER, password=PASSWORD, host=HOST, port=PORT)