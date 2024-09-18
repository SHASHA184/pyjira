# Task Tracker API

This is a task management API built using **FastAPI**. It allows users to create, retrieve, update, and delete tasks, with support for multiple assignees, role-based access control (RBAC), and email notifications when task statuses change.

## Features
- **User Roles**: Admin, Manager, and User.
- **Task Management**: Create, retrieve, update, and delete tasks.
- **Role-Based Access Control (RBAC)**: Different access levels based on roles.
- **Email Notifications**: Sends email updates when task statuses change.

## Tech Stack
- **FastAPI**: A modern, fast web framework for building APIs with Python 3.7+.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library.
- **Celery**: Distributed task queue for background job processing.
- **Pydantic**: Data validation and parsing using Python type annotations.
- **Alembic**: Database migrations tool for SQLAlchemy.

## Requirements

Ensure you have the following installed before running this application:
- Python 3.10+
- PostgreSQL
- Docker Compose

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/SHASHA184/pyjira
cd pyjira
```

### 2. Configure environment variables
Create a `.env` file in the root directory and add the following environment variables:
```bash
# Database configuration
DEFAULT_HOST=your_db_host
DEFAULT_USER=your_db_username
DEFAULT_PASSWORD=your_db_password
DEFAULT_DB=your_db_name
DEFAULT_PORT=your_db_port

# Email configuration
USE_MAILING=True                  # Enable or disable email notifications
MAIL_USERNAME=your_email_address
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email_address
MAIL_PORT=smtp_port
MAIL_SERVER=smtp_server_address
MAIL_FROM_NAME=your_name
MAIL_TLS=True                     # Enable TLS (True/False)
MAIL_SSL=False                    # Enable SSL (True/False)

# Authentication
SECRET_KEY=your_secret_key         # Key used for security and JWT token generation
```
Gmail Users: Setup for Email Notifications
If you want to use Gmail for sending email notifications, follow these steps:

Visit [Google Account Security Settings](https://myaccount.google.com/security) and enable 2-Step Verification.
Under 2-Step Verification, go to App Passwords and generate a new password for your app.
Use the generated 16-character password in the ```.env``` file as the ```MAIL_PASSWORD```.

### 3. Build Docker containers
To build and run the Docker containers:
```bash
docker-compose up -d --build
```

### 4. Run database migrations
To apply the initial database migrations:
```bash
docker-compose exec app alembic upgrade head
```

## Usage
### Access the API documentation
Once the server is running, you can access the API documentation via Swagger UI:
- Open your browser and go to `http://localhost:8000/docs`.

This interactive documentation allows you to test all API endpoints.

### User Authentication

1. Create a new user account by hitting the ```/users``` endpoint.
2. Log in using the ```/login``` endpoint and get an authorization token.
3. Use the **Authorize** button in the Swagger UI to pass the token for making authenticated requests.

## API Endpoints
Here’s a summary of available API endpoints:
### Users
- POST ```/users```: Create a new user.
- GET ```/users/{user_id}```: Retrieve user details by ID.
- PUT ```/users/{user_id}```: Update an existing user.
- DELETE ```/users/{user_id}```: Delete a user by ID.

### Tasks
- POST ```/tasks```: Create a new task.
- GET ```/tasks```: Retrieve all tasks (Admin/Manager).
- GET ```/tasks/{task_id}```: Retrieve task details by ID.
- PUT ```/tasks/{task_id}```: Update a task by ID.
- DELETE ```/tasks/{task_id}```: Delete a task by ID.