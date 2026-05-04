# Grievance Backend - Phase 1

A shared FastAPI backend serving two separate frontend applications:
1. **User/Citizen Portal** - For filing and tracking grievances
2. **Authority/Admin Dashboard** - For managing grievances and analytics

## Project Structure

```
grievance-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration & environment variables
│   ├── api/
│   │   ├── user_routes.py      # User portal endpoints (/api/user)
│   │   └── authority_routes.py # Authority dashboard endpoints (/api/authority)
│   ├── models/                 # SQLAlchemy ORM models (future)
│   ├── services/               # Business logic services (future)
│   ├── ml/                      # ML classification module (future)
│   ├── utils/                   # Utility functions & helpers (future)
│   └── db/                      # Database configuration (future)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── .gitignore                  # Git ignore rules
```

## API Endpoints

### Root
- `GET /` - Health check

### User Portal API
- `GET /api/user/health` - User API health check
- *More endpoints coming in Phase 2*

### Authority Dashboard API
- `GET /api/authority/health` - Authority API health check
- *More endpoints coming in Phase 2*

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd grievance-backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit `.env` file with your actual configuration:
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost/grievance_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secure-secret-key
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Role-Based Access Control (RBAC)

The backend implements role-based access control for three roles:

1. **USER** - Citizen/User Portal
   - Can view own grievances
   - Can file new grievances
   - Can track grievance status

2. **AUTHORITY** - Department Authority
   - Can view assigned grievances
   - Can update grievance status
   - Can add comments/notes

3. **ADMIN** - System Administrator
   - Full access to all grievances
   - Can manage users and authorities
   - Can view analytics and reports

*RBAC implementation to be added in Phase 2*

## Development Notes

- This is a **shared backend** - do not create separate backends for each frontend
- Always add routes to the appropriate router (`user_routes.py` or `authority_routes.py`)
- User routes should use the `/api/user` prefix
- Authority routes should use the `/api/authority` prefix
- Database models, services, and ML module structure are scoped for future phases

## CORS, JWT, and RBAC (Phase 2)

- **CORS:** The development server is configured to allow requests from common frontend dev servers (e.g. `http://localhost:3000` and `http://localhost:5173`). This enables browser-based frontends to call the backend during development.
- **JWT Settings:** Security-related settings such as `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` are loaded from environment variables in the `.env` file.
- **Single Shared Backend:** Both the User/Citizen frontend and Authority/Admin frontend will use this same backend. Keep user-facing routes under `/api/user` and authority routes under `/api/authority`.
- **RBAC:** Role-based access control for `USER`, `AUTHORITY`, and `ADMIN` roles will be added in a later phase.

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **sqlalchemy** - ORM for database operations
- **asyncpg** - PostgreSQL async driver
- **motor** - MongoDB async driver
- **redis** - Caching and session management
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **python-multipart** - Form data handling

## Next Steps

- Phase 2: Database models and migrations
- Phase 3: Authentication and authorization
- Phase 4: ML model integration
- Phase 5: API endpoint implementation
- Phase 6: Testing and documentation
