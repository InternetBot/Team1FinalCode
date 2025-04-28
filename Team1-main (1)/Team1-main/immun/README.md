# Immunization Records Management System

A full-stack web application for managing immunization records with user and admin roles.

## Features

- User authentication (login/register)
- User dashboard for uploading and viewing immunization records
- Admin dashboard for viewing all users' records
- Document upload support for immunization records
- Secure file storage and access control

## Tech Stack

- Frontend: React with Material-UI
- Backend: Flask (Python)
- Database: PostgreSQL
- Authentication: JWT
- Containerization: Docker

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd immunization-records
```

2. Build and start the containers:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Default Admin Account

To create an admin account, you can use the registration page and then update the user's `is_admin` field in the database to `true`.

## API Endpoints

### Authentication
- POST /api/auth/register - Register a new user
- POST /api/auth/login - Login user
- GET /api/auth/me - Get current user info

### Records
- POST /api/records/upload - Upload a new immunization record
- GET /api/records/my-records - Get user's records
- GET /api/records/all-records - Get all records (admin only)
- GET /api/records/document/{id} - Get record document

## Development

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

## Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens are used for authentication
- File uploads are validated and stored securely
- Admin-only routes are protected
- CORS is configured for security

## License

MIT License 