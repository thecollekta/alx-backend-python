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
│   ├── urls.py        # API endpoints
│   └── views.py       # View logic
├── messaging_app/     # Project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py    # Django settings
│   ├── urls.py        # Main URL routing
│   └── wsgi.py
├── .env.example       # Environment variable template
├── .gitignore
├── manage.py
├── README.md          # Project documentation
├── requirements.txt   # Dependencies file
└── settings.py        # Duplicated Django settings
```

## Request Logging Middleware

The application includes a custom middleware that logs all incoming requests to help with debugging and monitoring.

### Request Logging Features

* Logs each request with timestamp, username, and request path
* Automatically creates a `requests.log` file in the project root
* Handles both authenticated and anonymous users
* Logs are written in a human-readable format

### Log Format

Each log entry follows this format:

```text
YYYY-MM-DD HH:MM:SS.ssssss - User: [username] - Path: [request_path]
```

Example:

```bash
2025-07-26 14:37:49.123456 - User: admin - Path: /api/v1/conversations/
2025-07-26 14:38:12.456789 - User: Anonymous - Path: /api/v1/users/
2025-07-26 14:44:42.624159 - User: Anonymous - Path: /
2025-07-26 14:44:45.422102 - User: Anonymous - Path: /favicon.ico
2025-07-26 14:44:56.025656 - User: Anonymous - Path: /admin/
2025-07-26 14:44:56.139008 - User: Anonymous - Path: /admin/login/
```

### Log File Location

* Logs are stored in `requests.log` at the project root directory.

* The file is automatically created when the first request is made.

### Request Logging Configuration

The middleware is automatically enabled in `settings.py` and will start logging requests as soon as the server starts.

### Viewing Logs

To monitor logs in real-time, you can use:

```bash
tail -f requests.log  # Linux/Mac
Get-Content -Path .\requests.log -Wait  # Windows PowerShell
```

## Time-Based Access Restriction Middleware

The application includes a middleware that restricts access to chat features during specific hours to manage server load and user expectations.

### Time-Based Restriction Access Features

* Restricts access to chat endpoints between 9:00 PM and 6:00 AM (server time)
* Returns a 403 Forbidden response during restricted hours
* Provides a clear error message to users
* Logs all access attempts (including denied ones) via the Request Logging Middleware

### Time-Based Restriction Access (How It Works)

The `RestrictAccessByTimeMiddleware` checks the current server time for each request:

* If the time is between 9:00 PM and 6:00 AM, access is denied
* All other times, access is permitted
* The restriction applies to all endpoints in the application

### Error Response

When access is denied, the middleware returns:

```http
HTTP 403 Forbidden
Content-Type: text/plain

Access to the chat is restricted between 9:00 PM and 6:00 AM. Please try again during working hours.
```

### Time-Based Access Restriction Configuration

The middleware is automatically enabled in `settings.py` and is positioned after the `RequestLoggingMiddleware` in the middleware stack.

### Example Log Entries

```bash
2025-07-26 20:59:59.999999 - User: admin - Path: /api/v1/conversations/
2025-07-26 21:00:00.000001 - User: admin - Path: /api/v1/conversations/ [ACCESS DENIED]
2025-07-26 05:59:59.999999 - User: admin - Path: /api/v1/messages/ [ACCESS DENIED]
2025-07-26 06:00:00.000001 - User: admin - Path: /api/v1/messages/
```

## Offensive Language Middleware

The application includes a middleware that limits the number of chat messages a user can send within a specific time window, helping to prevent abuse and ensure fair usage.

### Features

* Limits each IP address to 5 message requests per minute
* Only applies to POST requests to message endpoints
* Automatically cleans up old request data
* Returns a 429 Too Many Requests response when the limit is exceeded

### Offensive Language (How It Works)

The `OffensiveLanguageMiddleware` tracks message submissions by IP address:

* Each IP can make up to 5 POST requests to message endpoints per minute
* The time window is a rolling 60-second period
* Old requests (older than 1 minute) are automatically removed from tracking
* The limit is applied per IP address to prevent abuse

### Offensive Language Error Response

When the rate limit is exceeded, the middleware returns:

```http
HTTP 429 Too Many Requests
Content-Type: application/json

{
    "error": "Rate limit exceeded. Please try again later.",
    "status": "error",
    "code": 429
}
```

### Offensive Language Configuration

The middleware is automatically enabled in `settings.py` and is positioned after the `OffensiveLanguageMiddleware` in the middleware stack.

### Example Usage

```bash
# First 5 requests within a minute
POST /api/v1/conversations/1/messages/  # 201 Created
POST /api/v1/conversations/1/messages/  # 201 Created
POST /api/v1/conversations/1/messages/  # 201 Created
POST /api/v1/conversations/1/messages/  # 201 Created
POST /api/v1/conversations/1/messages/  # 201 Created

# Sixth request within the same minute
POST /api/v1/conversations/1/messages/  # 429 Too Many Requests

# After 1 minute from the first request
POST /api/v1/conversations/1/messages/  # 201 Created (limit resets)
```

## Role-Based Permission Middleware

The application includes a middleware that enforces role-based access control (RBAC) for specific API endpoints, ensuring only authorized users can perform certain actions.

### Role-Based Permission Features

* Restricts access to protected endpoints based on user roles
* Different permission levels for different paths
* Clear error responses for unauthorized access attempts
* Seamless integration with Django's authentication system

### Protected Paths and Required Roles

| Endpoint | Allowed Roles | HTTP Methods | Description |
|----------|--------------|--------------|-------------|
| `/api/v1/users/` | `admin` | POST, PUT, PATCH, DELETE | User management endpoints |
| `/api/v1/conversations/` | `admin`, `moderator` | POST, PUT, PATCH, DELETE | Conversation management |

### Role-Based Permission (How It Works)

The `RolePermissionMiddleware`:

1. Checks if the requested path is protected
2. For protected paths and non-safe methods (POST, PUT, PATCH, DELETE):
   * Verifies user authentication
   * Checks if the user's role is in the allowed roles for the path
   * Blocks access with appropriate error if not authorized
3. Allows all GET, HEAD, and OPTIONS requests through for read operations

### Error Responses

**Unauthenticated User (401):**

```http
HTTP 401 Unauthorized
Content-Type: application/json

{
    "error": "Authentication required",
    "status": "error",
    "code": 401
}
```

**Insufficient Permissions (403):**

```http
HTTP 403 Forbidden
Content-Type: application/json

{
    "error": "Insufficient permissions. Admin or moderator role required.",
    "status": "error",
    "code": 403
}
```

### Configuration

The middleware is automatically enabled in `settings.py` and is positioned after the authentication-related middlewares in the middleware stack.

### Role-Based Permission Example Usage

1. **Admin Access (Allowed):**

   ```bash
   # As an admin
   curl -X DELETE http://localhost:8000/api/v1/users/3/ \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   # Returns 204 No Content (success)
   ```

2. **Regular User Access (Denied):**

   ```bash
   # As a regular user
   curl -X DELETE http://localhost:8000/api/v1/users/3/ \
     -H "Authorization: Bearer $USER_TOKEN"
   # Returns 403 Forbidden with error message
   ```

### Real-time Notifications

The application includes a notification system that automatically notifies users when they receive new messages. Notifications are created using Django signals and include:

* Automatic creation of notifications when new messages are sent
* Support for different notification types (message, mention, system)
* Mark notifications as read
* Efficient bulk creation for multiple recipients

#### Notification Model

```python
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('mention', 'Mention'),
        ('system', 'System Notification'),
    ]
    
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='message')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Signal Handler

Notifications are automatically created using Django's `post_save` signal:

```python
@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if not created:
        return

    participants = instance.conversation.participants.exclude(
        user_id=instance.sender.user_id
    )
    
    notifications = [
        Notification(user=participant, message=instance, notification_type='message')
        for participant in participants
    ]
    
    if notifications:
        Notification.objects.bulk_create(notifications)
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

### Notifications

| Endpoint          | Method | Description |
|-------------------|--------|-------------|
| `/notifications/` | GET | List all notifications for the current user |
| `/notifications/unread/` | GET | List unread notifications |
| `/notifications/{notification_id}/read/` | PATCH | Mark a notification as read |
| `/notifications/read-all/` | PATCH | Mark all notifications as read |

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

### 4. Testing Notifications

The test suite includes comprehensive tests for the notification system, covering:

* Notification creation when messages are sent
* No duplicate notifications on message updates
* Correct string representation
* Marking notifications as read
* No notifications for message senders

## Admin Interface

Access the admin interface at `http://127.0.0.1:8000/admin/` using admin credentials.

### Admin Features

* User management (create, edit, delete users)
* View all conversations
* Monitor messages
* User role management
* View all notifications
* Filter by notification type and read status
* Search by user details and message content
* View notification details including creation time

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

To run the test suite, including notification tests:

```bash
# Run all tests
python manage.py test

# Run only notification tests
python manage.py test chats.tests.NotificationSignalTests chats.tests.NotificationModelTests
```

### Creating Admin User

```bash
python manage.py createsuperuser
# Follow the prompts to create admin credentials
```

## License

This project is licensed under the ALX ProDEV Curriculum.
