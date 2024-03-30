# open-space-backend

## Описание

Этот проект представляет собой серверное приложение на Python, использующее FastAPI для создания веб-сервиса, а также базы данных PostgreSQL и хранилища данных Redis для хранения информации.

## Установка и настройка

1. **Склонируйте репозиторий:**
   ```bash
   git clone https://github.com/stand4r/open-space-backend.git
   cd open-space-backend
   ```

2. **Установите зависимости:**
   Запустите сервера
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройка базы данных:**
   - Создайте базу данных PostgreSQL и укажите параметры подключения в файле `config.py`.

5. **Запуск приложения:**
   ```bash
   uvicorn main:app --reload
   ```

## API Ресурсы

- `/api/users` - Ресурс для работы с пользователями.
- `/api/projects` - Ресурс для работы с проектами.
- `/api/auth` - Ресурс для работы с аутентификацией.
- `/api/feed` - Ресурс для работы с лентой.

## Используемые технологии

- Python 3.x
- FastAPI
- PostgreSQL
- Redis
- SMTP Yandex

## Структура проекта

```plaintext
open-space-backend-main/
│
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── PostgreDB.py
│   │   └── RedisDB.py
│   ├── mail/
│   │   ├── __init__.py
│   │   └── MailApi.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ProjectModel.py
│   │   └── UserModel.py
│   └── routers/
│   │   ├── __init__.py
│   │   ├── authenticationRouter.py
│   │   ├── projectsFeed.py
│   │   ├── projectsRouter.py
│   │   └── usersRouter.py
│
├── __init__.py
├── main.py
│
├── Pipfile
├── requirements.txt
└── README.md
```

## Дополнительная информация

Для тестов используйте http://127.0.0.1/docs

## Разработчики

- Дмитрий (@S_D6678) - sahojkodima888@gmail.com

## Лицензия

Этот проект лицензируется под MIT License - см. файл [LICENSE](LICENSE) для деталей.
