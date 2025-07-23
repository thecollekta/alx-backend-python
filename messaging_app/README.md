# Messaging App API

## Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate the environment:

   ```bash
   source .venv/scripts/activate # Windows
   source .venv/bin/activate # MacOS
   ```

3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
   * Follow the prompts to create admin account:

      ```bash
      python manage.py createsuperuser
      Email: <admin@example.com>
      First name: Admin
      Last name: User
      Password: ********
      Password (again): ********
      ```

6. Start development server: `python manage.py runserver`

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
* Django REST Framework 3.16.0+
* Python 3.12+
* djangorestframework-simplejwt (JWT Authentication)
* django-environ (for environment variables)
* django-filter (for API filtering)
* drf-nested-routers (for nested routes)
* psycopg (PostgreSQL adapter)

## Project Structure

```text
messaging_app/
├ .venv/             # Virtual environment
├ chats/             # Messaging app
| ├ migrations       # Database migrations
| ├ __init.py__.py
| ├ admin.py         # Admin panel config
| ├ apps.py
| ├ auth.py          # JWT Authentication settings
| ├ models.py        # Data models
| ├ permissions.py   # Custom permissions
| ├ serializers.py   # API serializers
| ├ tests.py
| ├ urls.py          # API endpoints
| ├ views.py         # View logic
├ messaging_app/     # Project config
| ├ __init__.py
| ├ asgi.py
| ├ settings.py
| ├ urls.py          # Main URL routing
| ├ wsgi.py
| ├ .env.example     # Environment variable template
├ .gitignore
├ manage.py
├ README.md          # Project documentation
├ requirements.txt   # Dependencies file
```

## Key Implementations

### Custom User Model

* Extended Django's AbstractUser with additional fields
* Email-based authentication (no username)
* UUID primary key instead of integer ID
* Role-based permissions (guest, host, admin)
* Fields:
  * first_name (required)
  * last_name (required)
  * email (unique, required)
  * phone_number (optional)
  * role (required, with choices)
  * created_at (auto timestamp)

### Conversation Model

* Many-to-Many relationship with Users
* UUID primary key
* Automatic creation timestamp
* Represents a messaging thread between multiple users

### Message Model

* ForeignKey relationship with Sender (User) and Conversation
* Text message body (required)
* Automatic sent timestamp
* UUID primary key

## API Endpoints

All endpoints are prefixed with `/api/v1/`

### Authentication

| Endpoint         | Method | Description                              |
|------------------|--------|------------------------------------------|
| `/token/`        | POST   | Obtain JWT token (access + refresh)      |
| `/token/refresh/`| POST   | Get new access token using refresh token |
| `/token/verify/` | POST   | Verify a token                           |

* Use DRF's session authentication or token authentication
* Login via browseable API: `/api-auth/login/`

### Users

* Admin Interface: `/admin/` to manage users, conversations, and messages

| Endpoint       | Method | Description                | Permissions        |
|----------------|--------|----------------------------|--------------------|
| `/users/`      | POST   | Register new user          | AllowAny           |
| `/users/me/`   | GET    | Get current user's profile | IsAuthenticated    |
| `/users/{id}/` | GET    | Get user details           | IsOwner or IsStaff |
| `/users/{id}/` | PATCH  | Update user details        | IsOwner or IsStaff |

### Conversations

|Endpoint        |Method     |Description| Permissions|
|----------------|-----------|-----------|------------|
| `/conversations/` |GET |List all conversations where current user is a participant |Authenticated|
| `/conversations/` |POST| Create new conversation (auto-adds current user) |Authenticated|
| `/conversations/{conversation_id}/` |GET |Retrieve conversation details with messages |Participant only|
| `/conversations/{conversation_id}/messages/`| GET |List all messages in conversation |Participant only|
| `/conversations/{conversation_id}/messages/`| POST| Create new message in conversation |Participant only|

**Filters**:

* Ordering: `?ordering=created_at` (or `-created_at` for descending)
* Search: `?search=term` (searches participant names/emails)

### Messages

|Endpoint        |Method     |Description| Permissions|
|----------------|-----------|-----------|------------|
| `/conversations/{conversation_id}/messages/` |GET |List all messages in conversation |Participant only|
| `/conversations/{conversation_id}/messages/` |POST |Send new message |Participant only|
| `/conversations/{conversation_id}/messages/{message_id}/` |GET |Retrieve specific message |Participant only|

**Filters**:

* Filter by sender role: ?sender__role=host
* Ordering: ?ordering=sent_at (or -sent_at for descending)
* Search: ?search=term (searches message body or sender names)

### Admin Panel Features

* Custom User management interface
* Conversation view with inline messages
* Message list with search and filters
* Role-based user management
* Relationship visualization

### Example Requests

#### User Registration

```bash
POST /api/v1/users/
{
  "username": "Collekta",
  "email": "admin@msgapp.com",   # Use your preferred email with domain
  "first_name": "Festus",
  "last_name": "Aboagye",
  "password": "AdminP@ss123",  
  "role": "admin" # host, guest options available. admin should not be exposed for user registration
}
```

#### User Login

```bash
POST /api/v1/token/
{
  "username": "Collekta",
  "password": "AdminP@ss123"
}
```

#### Create Conversation

```bash
POST /api/v1/conversations/
{
    "participant_ids": ["user-uuid-1", "user-uuid-2"]
}
```

#### Send Message

```bash
POST /api/v1/conversations/{conversation_id}/messages/
{
    "message_body": "Hello there!"
}
```

#### List Conversations

```bash
GET /api/v1/conversations/
```

#### List Messages in Conversation

```bash
GET /api/v1/conversations/{conversation_id}/messages/
```

## Security Considerations

* Always use HTTPS in production
* Tokens expire after 1 hour (configurable in settings)
* Refresh tokens expire after 1 day
* Passwords are hashed before storage
* Rate limiting is recommended for authentication endpoints

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface

Access the admin interface at `/admin/` using your superuser credentials.
