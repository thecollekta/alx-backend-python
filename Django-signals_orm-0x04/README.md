# Django Messaging System with Notifications

A robust messaging system built with Django that includes real-time notifications using Django signals. This application allows users to have conversations and get notified about new messages.

## Features

- **User Authentication**: Secure user registration and authentication
- **Conversations**: Create and manage conversations between users
- **Real-time Messaging**: Send and receive messages in conversations
- **Notifications**: Automatic notifications for new messages
- **RESTful API**: Built with Django REST Framework

## Models

### User

- Authentication and basic user information
- Related names: `sent_messages`, `received_messages`, `notifications`

### Conversation

- Groups of users in a conversation
- Fields: `conversation_id`, `participants`, `created_at`
- Related name: `messages`

### Message

- Individual messages within a conversation
- Fields: `message_id`, `sender`, `receiver`, `conversation`, `content`, `timestamp`
- Related name: `notifications`

### Notification

- Tracks message notifications for users
- Fields: `user`, `message`, `is_read`, `created_at`

## API Endpoints

### Authentication

- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Conversations

- `GET /api/conversations/` - List all conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}/` - Retrieve conversation details

### Messages

- `GET /api/conversations/{id}/messages/` - List messages in conversation
- `POST /api/conversations/{id}/messages/` - Send new message
- `PATCH /api/messages/{id}/` - Update message
- `DELETE /api/messages/{id}/` - Delete message

### Notifications

- `GET /api/notifications/` - List user notifications
- `PATCH /api/notifications/{id}/` - Mark notification as read

## Setup

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd Django-signals_orm-0x04
    ```

2. Create and activate virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run migrations:

    ```bash
    python manage.py migrate
    ```

5. Create superuser (optional):

    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Testing

Run the test suite with:

```bash
python manage.py test messaging.tests
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Security settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

## License

This project is licensed under the ALX ProDEV Curriculum.
