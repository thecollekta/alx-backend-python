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
   ```

## Dependencies

* Django 5.2.4+
* Django REST Framework
* Python 3.12+
* django-environ (for environment variables)

## Project Structure

```text
messaging_app/
├ .venv/             # Virtual environment
├ chats/             # Messaging app
| ├ migrations       # Database migrations
| ├ __init.py__.py
| ├ admin.py         # Admin panel config
| ├ apps.py
| ├ models.py
| ├ tests.py
| ├ views.py
├ messaging_app/     # Project config
| ├ __init__.py
| ├ asgi.py
| ├ settings.py
| ├ urls.py
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

### Admin Panel Features

* Custom User management interface
* Conversation view with inline messages
* Message list with search and filters
* Role-based user management
* Relationship visualization

## Endpoints (Development)

* Admin Interface: `http://localhost:8000/admin/`
* API Root (Coming soon)
