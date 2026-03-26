# HRMS Lite — Human Resource Management System

A lightweight HRMS for managing employees and tracking daily attendance.

## Tech Stack
- **Frontend**: React 18, Vite, React Router v6, Axios, React Hot Toast
- **Backend**: Django 4.2, Django REST Framework, django-cors-headers
- **Database**: SQLite (local) / PostgreSQL (production)
- **Deployment**: Vercel (frontend) · Render (backend)

## Running Locally

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
npm run dev
```

| Method                  | Endpoint                          | Description                            |
| ----------------------- | --------------------------------- | -------------------------------------- |
| GET, POST               | `/api/employees/`                 | List all employees / create employee   |
| GET, PUT, PATCH, DELETE | `/api/employees/{id}/`            | Retrieve / update / delete employee    |
| GET                     | `/api/departments/`               | List all departments                   |
| GET                     | `/api/dashboard/`                 | Get dashboard summary stats            |
| GET, POST               | `/api/attendance/`                | List attendance / mark attendance      |
| GET, PUT, PATCH, DELETE | `/api/attendance/{id}/`           | Retrieve / update / delete record      |
| GET                     | `/api/employees/{id}/attendance/` | Get attendance for a specific employee |


## Deployment
- Backend → **Render** (set `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`)
- Frontend → **Vercel** (set `VITE_API_BASE_URL` to your Render backend URL)