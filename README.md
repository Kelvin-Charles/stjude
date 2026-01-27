# ST Jude's Training Platform

A full-stack web application for ST Jude's training program with React frontend and Flask backend. Features authentication, role-based access control, and project tracking for students, mentors, and managers.

## Project Structure

```
stjude/
├── backend/              # Flask backend API
│   ├── app.py           # Main Flask application
│   ├── models.py        # Database models (User, Project, ProjectProgress)
│   ├── auth.py          # Authentication & authorization
│   ├── routes.py        # API routes
│   ├── projects/        # Student projects
│   └── requirements.txt
├── src/                 # React frontend
│   ├── contexts/        # React contexts (AuthContext)
│   ├── components/      # React components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── StudentDashboard.jsx
│   │   ├── MentorDashboard.jsx
│   │   └── ManagerDashboard.jsx
│   ├── App.jsx          # Main React component with routing
│   ├── main.jsx         # React entry point
│   └── index.css        # Tailwind CSS
└── package.json         # Frontend dependencies
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The backend will be available at `https://stjude.beetletz.online`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional, defaults to localhost:5000):
```bash
cp .env.example .env
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## User Roles

- **Student**: Can view and work on projects, track their progress
- **Mentor**: Can view all students, their progress, and provide feedback
- **Manager**: Can do everything mentors can, plus create new projects

## Default Admin Account

On first run, a default admin account is created:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Manager

**⚠️ Change this password in production!**

## API Endpoints

### Authentication
- `POST /api/register` - Register new user (requires: username, email, password, full_name, role)
- `POST /api/login` - Login (requires: username, password)
- `GET /api/me` - Get current user info (requires authentication)

### Projects (Authenticated)
- `GET /api/projects` - List all projects (includes user progress for students)
- `GET /api/projects/<project_id>` - Get project details

### Student Progress
- `GET /api/progress` - Get current student's progress (student only)
- `POST /api/progress` - Create/update project progress (student only)

### Mentor/Manager
- `GET /api/students` - List all students
- `GET /api/students/<student_id>/progress` - Get student's progress
- `POST /api/progress/<progress_id>/feedback` - Add feedback to student progress
- `GET /api/reports/overview` - Get overview report

### Manager Only
- `POST /api/admin/projects` - Create new project

### Other
- `GET /api/health` - Health check
- `GET /api/multiplication-table?max=13` - Generate multiplication table

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **User Management**: Register and manage students, mentors, and managers
- **Project Tracking**: Students can track their progress on projects
- **Progress Monitoring**: Mentors and managers can view student progress and provide feedback
- **Reports**: Overview reports for mentors and managers
- **React + Vite frontend** with Tailwind CSS
- **Flask REST API backend** with SQLite database
- **Role-based dashboards** for different user types

## Development

To run both frontend and backend simultaneously, use two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
python app.py
```

**Terminal 2 (Frontend):**
```bash
npm run dev
```
