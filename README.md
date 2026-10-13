# Hospital Appointment Booking System

## Project Overview

The Hospital Appointment Booking System is a backend application developed using FastAPI. It helps manage patients, doctors, departments, schedules, appointments, consultations, prescriptions, notifications, and audit logs.

The system provides JWT authentication, role-based access control, database migrations, appointment management, and automated testing.

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- Alembic
- JWT Authentication
- Passlib and bcrypt
- Pytest
- Uvicorn
- APScheduler
- ReportLab

## Features

- User registration and login
- JWT access-token authentication
- Access-token refresh and logout
- Role-based authorization
- Department management
- Doctor management
- Doctor schedules and leave management
- Appointment booking and rescheduling
- Appointment status management and history
- Consultations and prescriptions
- Prescription PDF generation
- Consultation file management
- Notifications and read-status management
- Audit logs
- Doctor ratings
- Doctor queue and WebSocket notifications
- Email and scheduled reminder support
- Reports and dashboard endpoints
- Database migrations using Alembic
- Automated tests using Pytest

## Project Structure

```text
Hospital-Appointment-Booking-System/
├── app/
│   ├── auth/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── database.py
│   └── main.py
├── alembic/
├── tests/
├── uploads/
├── screenshots/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9 or later
- MySQL Server
- pip

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/srinivasulu3679/Hospital-Appointment-Booking-System.git
cd Hospital-Appointment-Booking-System
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Configure the MySQL database connection, JWT settings, and email settings according to the variable names used by the application.

Do not commit `.env` or any passwords, secret keys, or access tokens to GitHub.

### 5. Run database migrations

```bash
python -m alembic upgrade head
```

### 6. Start the application

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at:

http://127.0.0.1:8000

## API Documentation

FastAPI Swagger UI:

http://127.0.0.1:8000/docs

OpenAPI schema:

http://127.0.0.1:8000/openapi.json

## Running Tests

Run the automated test suite:

```bash
python -m pytest -q
```

Latest recorded test result:

**53 passed**

The test suite passed in the local development environment. Deprecation warnings may appear depending on installed dependency versions.

## Database Migrations

Check the current migration:

```bash
python -m alembic current
```

Apply migrations:

```bash
python -m alembic upgrade head
```

## WebSocket Notifications

The application provides a WebSocket endpoint for user notifications:

```text
ws://127.0.0.1:8000/ws/notifications?token=ACCESS_TOKEN
```

Replace `ACCESS_TOKEN` with a valid access token obtained through login. Keep tokens private.

## Security Notes

- Store secrets in the local `.env` file.
- Keep `.env` and virtual-environment files out of GitHub.
- Use valid authentication tokens for protected endpoints.
- Configure email credentials securely.
- Do not upload real patient information or confidential files to the repository.

## Author

**Hospital Appointment Booking System**

Developed as a FastAPI backend project.