# Notes API - Complete Route Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication Routes

### 1. Register User
**POST** `/api/v1/auth/register`

**Description**: Create a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "password123"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses**:
- `400 Bad Request`: Email or username already exists
- `422 Unprocessable Entity`: Invalid input data

---

### 2. Login
**POST** `/api/v1/auth/login`

**Description**: Authenticate user and get access token

**Request Body** (form-data):
```
username=testuser&password=password123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Invalid input data

---

## 📝 Notes Routes

### 3. Create Note
**POST** `/api/v1/notes/`

**Description**: Create a new note for the authenticated user

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "My First Note",
  "content": "This is the content of my note",
  "is_public": false
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "My First Note",
  "content": "This is the content of my note",
  "is_public": false,
  "owner_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Invalid input data

---

### 4. Get User Notes
**GET** `/api/v1/notes/`

**Description**: Get all notes for the authenticated user

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `skip` (optional): Number of notes to skip (default: 0)
- `limit` (optional): Maximum number of notes to return (default: 100, max: 1000)

**Example**: `GET /api/v1/notes/?skip=0&limit=10`

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "My First Note",
    "content": "This is the content of my note",
    "is_public": false,
    "owner_id": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  },
  {
    "id": 2,
    "title": "Another Note",
    "content": "Another note content",
    "is_public": true,
    "owner_id": 1,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": null
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

---

### 5. Get Public Notes
**GET** `/api/v1/notes/public`

**Description**: Get all public notes (no authentication required)

**Query Parameters**:
- `skip` (optional): Number of notes to skip (default: 0)
- `limit` (optional): Maximum number of notes to return (default: 100, max: 1000)

**Example**: `GET /api/v1/notes/public?skip=0&limit=5`

**Response** (200 OK):
```json
[
  {
    "id": 2,
    "title": "Public Note",
    "content": "This is a public note",
    "is_public": true,
    "owner_id": 1,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": null
  }
]
```

---

### 6. Get Specific Note
**GET** `/api/v1/notes/{note_id}`

**Description**: Get a specific note by ID (user's own notes or public notes)

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `note_id` (integer): ID of the note to retrieve

**Example**: `GET /api/v1/notes/1`

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "My First Note",
  "content": "This is the content of my note",
  "is_public": false,
  "owner_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Note not found or not accessible

---

### 7. Update Note
**PUT** `/api/v1/notes/{note_id}`

**Description**: Update a specific note (only owner can update)

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters**:
- `note_id` (integer): ID of the note to update

**Request Body** (all fields optional):
```json
{
  "title": "Updated Note Title",
  "content": "Updated note content",
  "is_public": true
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated Note Title",
  "content": "Updated note content",
  "is_public": true,
  "owner_id": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Note not found or not owned by user
- `422 Unprocessable Entity`: Invalid input data

---

### 8. Delete Note
**DELETE** `/api/v1/notes/{note_id}`

**Description**: Delete a specific note (only owner can delete)

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `note_id` (integer): ID of the note to delete

**Example**: `DELETE /api/v1/notes/1`

**Response** (200 OK):
```json
{
  "message": "Note deleted successfully"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Note not found or not owned by user

---

## 📊 Complete Route Summary

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| POST | `/api/v1/auth/register` | No | Register new user |
| POST | `/api/v1/auth/login` | No | Login and get token |
| POST | `/api/v1/notes/` | Yes | Create new note |
| GET | `/api/v1/notes/` | Yes | Get user's notes |
| GET | `/api/v1/notes/public` | No | Get public notes |
| GET | `/api/v1/notes/{note_id}` | Yes* | Get specific note |
| PUT | `/api/v1/notes/{note_id}` | Yes | Update note |
| DELETE | `/api/v1/notes/{note_id}` | Yes | Delete note |

*Users can access their own notes or any public note

---

## 🔒 Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes**:
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

---

## 🧪 Testing Examples

### Using curl

1. **Register a user**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "testuser", "password": "password123"}'
```

2. **Login**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

3. **Create a note**:
```bash
curl -X POST "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Note", "content": "Note content", "is_public": false}'
```

4. **Get notes**:
```bash
curl -X GET "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Python requests

```python
import requests

# Register
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "user@example.com",
    "username": "testuser", 
    "password": "password123"
})

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "testuser",
    "password": "password123"
})
token = response.json()["access_token"]

# Create note
headers = {"Authorization": f"Bearer {token}"}
response = requests.post("http://localhost:8000/api/v1/notes/", 
    headers=headers,
    json={"title": "My Note", "content": "Content", "is_public": False}
)
```

---

## 📝 Notes on Idempotency

- **GET requests**: Always idempotent
- **POST requests**: Idempotent for user registration (duplicate email/username returns error)
- **PUT requests**: Idempotent (same request produces same result)
- **DELETE requests**: Idempotent (deleting non-existent note returns 404)

## 🔄 Race Condition Mitigation

The API includes protection against race conditions in note updates through:
- Database constraints and unique indexes
- Proper error handling for concurrent modifications
- Clear error messages for conflict resolution
