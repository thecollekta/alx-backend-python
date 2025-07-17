# Messaging App API

## Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate the environment:

   ```bash
    source .venv/scripts/activate # Windows
    source .venv/bin/activate # MacOS
   ```

3. Install dependacies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

## Dependencies

- Django 5.2.4+
- Django REST Framework

## Project Structure

```text
messaging_app/
├ .venv/            # Virtual environment
├ chats/            # messaging app
| ├ migrations
| ├ __init.py__.py
| ├ admin.py
| ├ apps.py
| ├ models.py
| ├ tests.py
| ├ views.py
├ messaging_app/    # Project config folder
| ├ __init__.py
| ├ asgi.py
| ├ settings.py
| ├ urls.py
| ├ wsgi.py
| ├ .env.example            # Environment variable
├ .gitignore
├ manage.py
├ README.md         # Project documentation
├ requirements.txt  # Dependencies file
```
