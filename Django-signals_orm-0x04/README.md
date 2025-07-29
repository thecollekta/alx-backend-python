# Django Messaging System with Notifications

A robust messaging system built with Django that includes real-time notifications using Django signals. This application allows users to have conversations and get notified about new messages

---

## Features

- **User Authentication**: Secure user registration and authentication
- **Conversations**: Create and manage conversations between users
- **Real-time Messaging**: Send and receive messages in conversations
- **Message History**: Track and view complete edit history of messages
- **Notifications**: Automatic notifications for new messages
- **Account Deletion**: Delete user account and associated data
- **RESTful API**: Built with Django REST Framework

---

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
- Fields: `message_id`, `sender`, `receiver`, `conversation`, `content`, `timestamp`, `edited`
- Related names: `notifications`, `history`
- The `edited` flag indicates if the message has been modified

### MessageHistory

- Tracks all edits made to messages
- Fields: `message` (FK to Message), `content` (previous content), `edited_at`, `edited_by` (FK to User)
- Ordered by `edited_at` in descending order

### Notification

- Tracks message notifications for users
- Fields: `user`, `message`, `is_read`, `created_at`

---

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
- `PATCH /api/messages/{id}/` - Update message (automatically tracks edit history)
- `DELETE /api/messages/{id}/` - Delete message
- `GET /api/messages/{id}/history/` - View edit history of a message

### Notifications

- `GET /api/notifications/` - List user notifications
- `PATCH /api/notifications/{id}/` - Mark notification as read

### User Account

- `DELETE /api/user/delete/` - Delete the authenticated user's account and all associated data
  - Requires authentication
  - Automatically cleans up all user-related data including:
    - Messages (sent and received)
    - Notifications
    - Message edit history

---

## Message Edit History

The application automatically tracks all edits made to messages:

- Each time a message is edited, the previous version is saved to the `MessageHistory` model
- The `edited` flag on the Message model is automatically set to `True` when content is modified
- Edit history includes:
  - Previous content
  - Timestamp of edit
  - User who made the edit

### Viewing Edit History

Edit history can be viewed:

1. Through the Django admin interface
2. Via the API endpoint: `GET /api/messages/{id}/history/`
3. Each history entry shows the previous content and when/why it was changed

---

## Account Management

### Account Deletion

Users can delete their accounts, which automatically triggers cleanup of all their data:

1. **What Gets Deleted**:
   - User account
   - All messages sent or received by the user
   - All notifications related to the user
   - All message history entries where the user was the editor

2. **How It Works**:
   - Uses Django's `post_delete` signal for clean data removal
   - Ensures referential integrity with proper cascade deletion
   - Performs cleanup in a transaction to maintain data consistency

3. **Security**:
   - Only authenticated users can delete their own accounts
   - Operation is irreversible
   - Protected against CSRF attacks

---

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

---

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

---

## License

This project is licensed under the ALX ProDEV Curriculum.
