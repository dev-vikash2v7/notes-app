# Notes API - FastAPI CRUD Application

A minimal but production-ready CRUD API for notes with JWT authentication, built with FastAPI.

## 🚀 Features

- **Authentication**: JWT-based authentication with secure password hashing
- **CRUD Operations**: Full Create, Read, Update, Delete for notes
- **Authorization**: Users can only access their own notes (plus public notes)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Validation**: Request/response validation with Pydantic
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Idempotency**: Operations are designed to be idempotent

## 🏗️ Architecture

### Framework Choice: FastAPI
- **Fast**: Built on Starlette and Pydantic, offering high performance
- **Modern**: Type hints, async/await support, automatic validation
- **Developer Experience**: Automatic API documentation, IDE support
- **Production Ready**: Built-in security, CORS, middleware support

### Authentication: JWT (JSON Web Tokens)
- **Stateless**: No server-side session storage required
- **Scalable**: Works well with microservices and load balancers
- **Industry Standard**: Widely adopted and well-understood
- **Security**: Tokens expire automatically, can be revoked if needed

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🛣️ API Routes

### Authentication Routes
| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| POST | `/api/v1/auth/register` | Register new user | `{"email": "user@example.com", "username": "user", "password": "password"}` | User object |
| POST | `/api/v1/auth/login` | Login and get token | `{"username": "user", "password": "password"}` | `{"access_token": "jwt_token", "token_type": "bearer"}` |

### Notes Routes
| Method | Path | Description | Auth Required | Request Body | Response |
|--------|------|-------------|---------------|--------------|----------|
| POST | `/api/v1/notes/` | Create new note | Yes | `{"title": "Note Title", "content": "Note content", "is_public": false}` | Note object |
| GET | `/api/v1/notes/` | Get user's notes | Yes | - | Array of notes |
| GET | `/api/v1/notes/public` | Get public notes | No | - | Array of notes |
| GET | `/api/v1/notes/{note_id}` | Get specific note | Yes* | - | Note object |
| PUT | `/api/v1/notes/{note_id}` | Update note | Yes | `{"title": "New Title", "content": "New content"}` | Note object |
| DELETE | `/api/v1/notes/{note_id}` | Delete note | Yes | - | `{"message": "Note deleted successfully"}` |

*Users can access their own notes or any public note

## 🔒 Failure Mode & Mitigation

### Race Condition: Concurrent Note Updates

**Problem**: Two users or processes updating the same note simultaneously could lead to lost updates.

**Example Scenario**:
1. User A fetches note (version 1)
2. User B fetches note (version 1)
3. User A updates note (version 2)
4. User B updates note (overwrites User A's changes)

**Mitigation Strategy**: Optimistic Locking with Version Control

```python
# Enhanced Note model with version control
class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(Integer, default=1)  # Version control
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Update operation with version check
def update_note_with_version(db: Session, note_id: int, note_update: NoteUpdate, user_id: int, expected_version: int) -> Note:
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if db_note.version != expected_version:
        raise HTTPException(
            status_code=409, 
            detail="Note has been modified by another user. Please refresh and try again."
        )
    
    update_data = note_update.dict(exclude_unset=True)
    update_data["version"] = expected_version + 1
    
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note
```

**Benefits**:
- Prevents lost updates
- Provides clear error messages to users
- Maintains data consistency
- Minimal performance overhead

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Installation

1. **Clone and setup**:
```bash
git clone <repository>
cd notes-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database setup**:
```bash
# Create PostgreSQL database
createdb notes_db

# Run migrations (if using Alembic)
alembic upgrade head
```

3. **Environment variables**:
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/notes_db
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. **Run the application**:
```bash
uvicorn app.main:app --reload
```

5. **Access the API**:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing the API

### 1. Register a user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "testuser", "password": "password123"}'
```

### 2. Login and get token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 3. Create a note
```bash
curl -X POST "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Note", "content": "This is the content of my note", "is_public": false}'
```

### 4. Get user's notes
```bash
curl -X GET "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```


