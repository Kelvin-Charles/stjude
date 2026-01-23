# Flask Backend for ST Jude's Training

This is the Flask backend API for the ST Jude's Training application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or if using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns server health status

### Multiplication Table
- **GET** `/api/multiplication-table?max=13`
- Generates a multiplication table
- Query parameter `max` (default: 13, max: 100)

### List Projects
- **GET** `/api/projects`
- Returns list of all available projects

### Get Project
- **GET** `/api/projects/<project_name>`
- Returns details and files for a specific project

### Verify Password
- **POST** `/api/students/verify-password`
- Body: `{"password": "onlydadas"}`
- Verifies password for student sign-in sheet access

## Example Usage

```bash
# Health check
curl http://localhost:5000/api/health

# Get multiplication table
curl http://localhost:5000/api/multiplication-table?max=12

# List projects
curl http://localhost:5000/api/projects

# Verify password
curl -X POST http://localhost:5000/api/students/verify-password \
  -H "Content-Type: application/json" \
  -d '{"password": "onlydadas"}'
```
