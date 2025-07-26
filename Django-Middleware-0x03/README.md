# Messaging App API

## Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate the environment:

   ```bash
   source .venv/scripts/activate  # Windows
   source .venv/bin/activate     # MacOS/Linux
   ```

3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations: `python manage.py migrate`
5. Create test data: `python manage.py create_test_data`
6. Create admin user: `python manage.py createsuperuser`
7. Start development server: `python manage.py runserver`

## Environment Configuration

1. Create .env file from template:

   ```bash
   cp .env.example .env
   ```

2. Set required values:

   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

## Dependencies

* Django 5.2.4+
* Django REST Framework 3.14.0+
* djangorestframework-simplejwt (JWT Authentication)
* django-environ (for environment variables)
* django-filter (for API filtering)
* psycopg2-binary (PostgreSQL adapter)
* python-dotenv (for local development)

## Project Structure

```text
messaging_app/
├── .venv/             # Virtual environment
├── chats/             # Messaging app
│   ├── migrations/    # Database migrations
│   ├── management/    # Custom management commands
│   ├── __init__.py
│   ├── admin.py       # Admin panel config
│   ├── apps.py
│   ├── models.py      # Data models
│   ├── permissions.py # Custom permissions
│   ├── serializers.py # API serializers
│   ├── urls.py       # API endpoints
│   └── views.py      # View logic
├── messaging_app/     # Project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py   # Django settings
│   ├── urls.py      # Main URL routing
│   └── wsgi.py
├── .env.example     # Environment variable template
├── .gitignore
├── manage.py
├── README.md        # Project documentation
└── requirements.txt # Dependencies file
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Obtaining Tokens

1. **Get Access Token**:

   ```bash
   POST /api/v1/token/
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. **Using the Token**:
   Include the token in the Authorization header:

   ```bash
   Authorization: Bearer your_token_here
   ```

3. **Refresh Token**:

   ```bash
   POST /api/v1/token/refresh/
   {
     "refresh": "your_refresh_token_here"
   }
   ```

## Permissions

* **IsAuthenticated**: Required for all API endpoints
* **IsParticipantOfConversation**: Users must be participants to view/modify conversations
* **IsMessageOwnerOrReadOnly**: Only message owners can edit/delete their messages
* **IsAdminUser**: Required for admin interface access

## API Endpoints

### Token Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/token/` | POST | Obtain JWT token (access + refresh) |
| `/token/refresh/` | POST | Get new access token using refresh token |
| `/token/verify/` | POST | Verify a token |

### Users

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/users/` | POST | Register new user | AllowAny |
| `/users/me/` | GET | Get current user's profile | IsAuthenticated |
| `/users/{id}/` | GET | Get user details | IsOwner or IsStaff |
| `/users/{id}/` | PATCH | Update user details | IsOwner or IsStaff |

### Conversations

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/conversations/` | GET | List user's conversations | IsAuthenticated |
| `/conversations/` | POST | Create new conversation | IsAuthenticated |
| `/conversations/{id}/` | GET | Get conversation details | IsParticipant |
| `/conversations/{id}/messages/` | GET | List messages | IsParticipant |
| `/conversations/{id}/messages/` | POST | Send new message | IsParticipant |

### Messages

#### List Messages in a Conversation

```http
GET /api/v1/conversations/{conversation_id}/messages/
```

**Pagination**:

* Returns 20 messages per page by default
* Use `page` parameter to navigate through pages
* Customize page size with `page_size` parameter (max 100)

**Filtering**:

* `sender`: Filter by sender ID or username
* `start_date`: Filter messages sent after this date (YYYY-MM-DD HH:MM:SS)
* `end_date`: Filter messages sent before this date (YYYY-MM-DD HH:MM:SS)
* `search`: Search in message content (case-insensitive)

**Sorting**:

* Use `ordering` parameter with:
  * `sent_at` (ascending)
  * `-sent_at` (descending, default)
  * `sender__username` (alphabetical by sender)
  * `-sender__username` (reverse alphabetical by sender)

**Example Request**:

```bash
# Get first page of messages from conversation 1, ordered by most recent
GET /api/v1/conversations/{conversation_id}/messages/

# Get second page with 10 messages per page
GET /api/v1/conversations/{conversation_id}/messages/?page=2&page_size=10

# Filter messages from a specific sender
GET /api/v1/conversations/{conversation_id}/messages/?sender=kwame

# Search for messages containing "hello"
GET /api/v1/conversations/{conversation_id}/messages/?search=hello

# Get messages from a date range
GET /api/v1/conversations/{conversation_id}/messages/?start_date=2025-07-01&end_date=2025-07-23

# Combine filters
GET /api/v1/conversations/{conversation_id}/messages/?sender=kwame&start_date=2025-07-01&search=hello
```

**Example Response**:

```json
{
  "links": {
    "next": "http://api.example.org/conversations/{conversation_id}/messages/?page=2",
    "previous": null
  },
  "count": 42,
  "total_pages": 3,
  "current_page": 1,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "message_body": "Hello, how are you?",
      "sent_at": "2025-07-01T12:00:00Z",
      "sender": {
        "id": 1,
        "username": "kwame",
        "first_name": "Kwame",
        "last_name": "Mensah"
      }
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "message_body": "I'm doing well, thanks!",
      "sent_at": "2025-07-01T12:05:00Z",
      "sender": {
        "id": 2,
        "username": "ama",
        "first_name": "Ama",
        "last_name": "Agyei"
      }
    }
  ]
}
```

## API Documentation

### 1. Message API Overview

The Message API provides endpoints for managing conversations and messages with features like authentication, pagination, filtering, and permission controls. It uses JWT for authentication and follows RESTful principles.

### 2. Authentication Tests

#### 2.1 Get JWT Token

**Description**:
This endpoint authenticates users and returns JWT tokens for accessing protected endpoints. The access token should be included in the `Authorization` header for subsequent requests.

**Endpoint**: `POST /api/v1/token/`

**Request Body**:

```json
{
    "username": "string",
    "password": "string"
}
```

**Response**:

* 200 OK: Returns access and refresh tokens
* 401 Unauthorized: Invalid credentials

**Usage**:

* First step in the authentication flow
* Tokens expire after 1 hour (configurable)
* Use refresh token to get new access tokens

### 3. Conversation Tests

#### 3.1 Create a New Conversation

**Description**:
Creates a new conversation between the authenticated user and specified participants. The creator is automatically added as a participant.

**Endpoint**: `POST /api/v1/conversations/`

**Headers**:

* `Authorization: Bearer <token>`
* `Content-Type: application/json`

**Request Body**:

```json
{
    "participants": [2, 3]
}
```

**Response**:

* 201 Created: Returns the created conversation
* 400 Bad Request: Invalid participant data
* 401 Unauthorized: Missing or invalid token

### 4. Message Tests

#### 4.1 Send a Message

**Description**:
Sends a new message to a specified conversation. The sender is automatically set to the authenticated user.

**Endpoint**: `POST /api/v1/conversations/{conversation_id}/messages/`

**Headers**:

* `Authorization: Bearer <token>`
* `Content-Type: application/json`

**Request Body**:

```json
{
    "message_body": "Your message here"
}
```

**Response**:

* 201 Created: Returns the created message
* 403 Forbidden: User is not a participant in the conversation
* 404 Not Found: Conversation does not exist

#### 4.2 List Messages with Pagination

**Description**:
Retrieves messages from a conversation with pagination support. Returns 20 messages per page by default.

**Endpoint**: `GET /api/v1/conversations/{conversation_id}/messages/`

**Query Parameters**:

* `page`: Page number (default: 1)
* `page_size`: Number of messages per page (default: 20, max: 100)

**Response**:

* 200 OK: Returns paginated list of messages
* 403 Forbidden: User is not a participant
* 404 Not Found: Conversation does not exist

### 5. Permission Tests

#### 5.1 Test Unauthorized Access

**Description**:
Verifies that protected endpoints reject requests without valid authentication.

**Test Cases**:

* Access any protected endpoint without token
* Expected: 401 Unauthorized
* Purpose: Ensures security of protected resources

#### 5.2 Test Access to Other User's Conversation

**Description**:
Verifies that users can only access conversations they participate in.

**Test Flow**:

1. User A creates a conversation
2. User B attempts to access User A's conversation
3. Expected: 403 Forbidden

**Purpose**:

* Validates conversation privacy
* Ensures proper access control implementation

### 6. Filtering

#### 6.1 Filter Messages by Date Range

**Description**:
Retrieves messages sent within a specific date range.

**Endpoint**: `GET /api/v1/conversations/{conversation_id}/messages/`

**Query Parameters**:

* `start_date`: Messages sent after this datetime (ISO 8601 format)
* `end_date`: Messages sent before this datetime (ISO 8601 format)

**Example**:

```text
GET /api/v1/conversations/1/messages/?start_date=2023-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z
```

**Response**:

* 200 OK: Returns filtered messages
* 400 Bad Request: Invalid date format
* 403 Forbidden: User is not a participant

**Usage**:

* Useful for retrieving messages from a specific time period
* Supports timezone-aware datetime strings
* Can be combined with other filters and pagination

## Test Data

Pre-created test users:

1. **Kwame Mensah**
   * Username: `kwame`
   * Password: `testpass123`

2. **Ama Agyei**
   * Username: `ama`
   * Password: `testpass123`

3. **Kofi Asante**
   * Username: `kofi`
   * Password: `testpass123`

**Note**: Kwame and Ama share a conversation with test messages in Twi.

## Testing Permissions

### 1. Unauthenticated Access (401)

```bash
curl -X GET http://127.0.0.1:8000/api/v1/conversations/
# Should return 401 Unauthorized
```

### 2. Non-Participant Access (403)

```bash
# Get Kofi's token
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kofi", "password": "testpass123"}' | jq -r '.access')

# Try to access Kwame and Ama's conversation
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/v1/conversations/1/
# Should return 403 Forbidden
```

### 3. Message Operations

```bash
# Get Kwame's token
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kwame", "password": "testpass123"}' | jq -r '.access')

# Try to edit Ama's message (should fail)
curl -X PATCH http://127.0.0.1:8000/api/v1/conversations/{conversation_id}/messages/2/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message_body": "Edited message"}'
# Should return 403 Forbidden
```

## Admin Interface

Access the admin interface at `http://127.0.0.1:8000/admin/` using admin credentials.

### Admin Features

* User management (create, edit, delete users)

* View all conversations
* Monitor messages
* User role management

## Security Considerations

* Always use HTTPS in production
* Tokens expire after 1 hour (configurable in settings)
* Refresh tokens expire after 1 day
* Passwords are hashed before storage
* Admin interface is protected by `IsAdminUser`
* Rate limiting recommended for authentication endpoints

## Development

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Tests

```bash
python manage.py test
```

### Creating Admin User

```bash
python manage.py createsuperuser
# Follow the prompts to create admin credentials
```

## License

This project is licensed under the ALX ProDEV Curriculum.
