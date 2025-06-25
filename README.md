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

## 🚀 Начало работы

### 🔧 Установка и запуск проекта

```bash
# Клонировать репозиторий
git clone https://github.com/yourusername/library-api.git
cd library-api

# Создать и активировать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # для Unix
# .venv\Scripts\activate    # для Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить .env файл
cp .env.example .env
# Измените параметры в .env при необходимости

# Выполнить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
