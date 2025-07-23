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
curl -X PATCH http://127.0.0.1:8000/api/v1/conversations/1/messages/2/ \
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
