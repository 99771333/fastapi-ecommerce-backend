# FastAPI E-Commerce Backend

A backend application for an e-commerce system built using Python and FastAPI.

## Features

- User registration and login
- Password hashing
- JWT-based authentication
- JWT access token expiration
- Product CRUD APIs
- PostgreSQL database integration
- SQLAlchemy ORM
- Alembic database migrations
- API testing through Swagger UI

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- Pydantic
- Git and GitHub

## API Documentation

After running the application, open Swagger UI:

http://127.0.0.1:8001/docs

## Project Status

Currently under development. More features and improvements will be added.

## Authors

Yash Koushal


## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/99771333/fastapi-ecommerce-backend.git
cd fastapi-ecommerce-backend
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv myvenv
myvenv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure:

```env
DATABASE_URL=your_database_connection_string
SECRET_KEY=your_random_secret_key
```

Use your own PostgreSQL connection string and a strong, randomly generated secret key. Do not commit the `.env` file.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the development server

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Open Swagger UI at:

http://127.0.0.1:8001/docs