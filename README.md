# 📚 Library API

RESTful API для управления библиотечным каталогом. Поддерживает регистрацию библиотекарей, аутентификацию через JWT, CRUD-операции с книгами и читателями, а также бизнес-логику по выдаче и возврату книг.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Build](https://img.shields.io/badge/build-passing-blue)
![Coverage](https://img.shields.io/badge/tests%25-success)



## 🧰 Технологии

- Python 3.12+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic v2
- Uvicorn
- pyjwt
- passlib[bcrypt]
- Pytest
- Docker / Docker Compose
- poetry (управление зависимостями)

---

## Запуск приложения

Для запуска приложения требуется установленный Docker и Docker Compose.
1. Клонируйте репозиторий:
```
git clone https://github.com/AlexeyPetrochenko/rest-api-for-library
cd rest-api-for-library
```

2. Создайте файл `.env` на основе `.test_env`.
- `.test_env` - удалять не требуется он нужен для запуска интеграционных тестов на тестовой БД.
- Пропишите параметры подключения к БД, секретный ключ, конфигурацию JWT и прочее.

3. Запустите контейнеры:
```
docker compose up --build
```
- Откройте документацию OpenAPI:
http://localhost:8000/docs

## Тестирование
Для запуска тестов необходимо:

1. Установить зависимости:
```
python3 -m venv .venv
source .venv/bin/activate
poetry install
```
2. Поднимите тестовую БД:
```
docker compose up test_db -d
```
3. Запустите тесты:
```
python3 -m pytest .
```

## Команда проекта
* Алексей Петроченко — Backend-разработчик
Тестовое задание для стажёра Python
Контакты: GitHub | Telegram | alexeypetrochenko1@gmail.com
