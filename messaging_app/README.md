# Messaging App API

A Django REST API for messaging functionality with JWT authentication, conversation management, and message filtering capabilities.

## Quick Start with Docker Compose

The fastest way to get the application running is with Docker Compose:

### Prerequisites

- Docker Engine installed ([Installation Guide](https://docs.docker.com/engine/install/))
- Docker Compose installed (usually included with Docker Desktop)

### Data Persistence

The application uses Docker volumes to ensure data persistence:

- **Database data**: Stored in `mysql_data` volume (persists across container restarts)
- **Static files**: Stored in `static_volume` volume
- **Media files**: Stored in `media_volume` volume

These volumes are preserved even when containers are stopped. To completely remove data, use `docker-compose down -v`.

### Setup Instructions

1. **Clone the repository and navigate to the project directory**:

    ```bash
    git clone <repository-url>
    cd messaging_app
    ```

2. **Set up environment variables**:

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file with your preferred database credentials and settings.

3. **Build and start the services**:

    ```bash
    docker-compose up --build
    ```

   This will:
   - Build the Django application image
   - Start a MySQL database container
   - Apply database migrations
   - Create a superuser (admin) account
   - Start the development server on `http://localhost:8000`

4. **Access the application**:
   - API: `http://localhost:8000/api/v1/`
   - Admin Panel: `http://localhost:8000/admin/`
   - Default admin credentials: `admin` / `admin123`

5. **Stop services when done**:

    ```bash
    docker-compose down
    ```

### Docker Commands

```bash
# Build only the web service
docker-compose build web

# Start services in detached mode
docker-compose up -d

# View logs
docker-compose logs web
docker-compose logs db

# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py createsuperuser

# Stop and remove containers, networks, and volumes
docker-compose down -v
```

---

## Kubernetes Local Setup

This project includes a script to set up a local Kubernetes cluster for development and testing purposes using Minikube.

### Kubernetes (Prerequisites)

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Docker](https://docs.docker.com/get-docker/)

### Using kurbeScript

The `kurbeScript` automates the setup and verification of a local Kubernetes cluster.

#### Kubernetes Features

- Automatic cluster startup with configurable resources
- System requirement validation
- Resource availability checks
- Color-coded output for better readability
- Detailed error handling and troubleshooting

### Basic Usage

```bash
# Make the script executable
chmod +x kurbeScript

# Run with default settings:
./kurbeScript

# For help and available options:
./kurbeScript --help
```

This will:

- Start a Kubernetes cluster using Minikube (with default settings: driver=docker, cpus=2, memory=2000mb)
- Verify the cluster is running
- Show the pods in the cluster

### Custom Configuration (Optional)

You can customize the cluster configuration using command-line arguments:

```bash
# Example: Create cluster with custom resources
./kurbeScript --driver docker --cpus 4 --memory 4096mb
```

Available options:

- `--driver`: Container runtime (docker, virtualbox, podman, ssh)
- `--cpus`: Number of CPUs to allocate (default: 2)
- `--memory`: Memory to allocate (default: 2000mb)

### Verifying the Setup

After successful execution, the script will:

1. Start the Minikube cluster
2. Verify the cluster status
3. Display running pods in all namespaces

### Accessing the Cluster

```bash
# Open Kubernetes dashboard
minikube dashboard

# Get cluster info:
kubectl cluster-info
```

### Troubleshooting

Common issues and solutions:

1. **Insufficient memory**:
   - Reduce requested memory: `--memory 1500mb`
   - Close other memory-intensive applications

2. **Driver issues**:
   - Try a different driver: `--driver virtualbox`, `--driver podman`, `--driver ssh`
   - Ensure the selected driver is properly installed

3. **Cluster startup failures**:

    ```bash
    # View detailed logs:
    minikube logs

    # Resetting the cluster
    minikube delete
    ./kurbeScript
    ```

### Notes

- The script includes error checking and will provide troubleshooting tips if cluster startup fails.
- By default, it uses the Docker driver. If you encounter issues, try switching to a different driver.
- Ensure your system meets the resource requirements for the requested cluster configuration.

---

## Kubernetes Deployment

### Kubernetes Deployment (Prerequisites)

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured
- Docker image built and pushed to registry

### Deployment Files

The project includes these Kubernetes configuration files:

- `deployment.yaml`: Main app deployment with services and configs
- `db-deployment.yaml`: PostgreSQL database configuration

### Deployment Guide

**Prerequisites**:

- Docker installed
- Minikube installed
- kubectl installed
- Docker Hub account (for registry access)

1. Build and Push Docker Image

    ```bash
    # Navigate to project directory
    cd messaging_app

    # Build Docker image
    docker build -t messaging-app:1.0.0 .

    # Authenticate to Docker Hub
    docker login

    # Tag and push to registry
    docker tag messaging-app:1.0.0 <your-dockerhub-username>/messaging-app:1.0.0
    docker push <your-dockerhub-username>/messaging-app:1.0.0
    ```

2. Prepare Kubernetes Environment

    ```bash
    # Start Minikube cluster
    minikube start

    # Enable registry addon
    minikube addons enable registry

    # Set up Docker environment
    eval $(minikube docker-env)
    ```

3. Deploy Database (PostgreSQL)
Create db-deployment.yaml:

    ```bash
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: postgres
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: postgres
    template:
        metadata:
        labels:
            app: postgres
        spec:
        containers:
        - name: postgres
            image: postgres:17
            resources:
            requests:
                memory: "256Mi"
                cpu: "250m"
            limits:
                memory: "512Mi"
                cpu: "500m"
            env:
            - name: POSTGRES_DB
            valueFrom:
                secretKeyRef:
                name: messaging-app-secrets
                key: DB_NAME
            - name: POSTGRES_USER
            valueFrom:
                secretKeyRef:
                name: messaging-app-secrets
                key: DB_USER
            - name: POSTGRES_PASSWORD
            valueFrom:
                secretKeyRef:
                name: messaging-app-secrets
                key: DB_PASSWORD
            ports:
            - containerPort: 5432
            volumeMounts:
            - mountPath: /var/lib/postgresql/data
            name: postgres-data
        volumes:
        - name: postgres-data
            persistentVolumeClaim:
            claimName: postgres-pvc
    ---
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
    name: postgres-pvc
    spec:
    accessModes:
        - ReadWriteOnce
    resources:
        requests:
        storage: 1Gi
    ---
    apiVersion: v1
    kind: Service
    metadata:
    name: db-service
    spec:
    selector:
        app: postgres
    ports:
        - protocol: TCP
        port: 5432
        targetPort: 5432
    ```

    Apply database configuration:

    ```bash
    kubectl apply -f db-deployment.yaml
    ```

4. Deploy Django Application

    ```bash
    # Update image reference in deployment.yaml
    sed -i 's|localhost:5000/messaging-app:1.0.0|<your-dockerhub-username>/messaging-app:1.0.0|' deployment.yaml

    # Apply Kubernetes configuration
    kubectl apply -f deployment.yaml

    # Verify deployment
    kubectl get pods --watch
    kubectl get all
    kubectl logs -f deployment/messaging-app
    ```

5. Access the Application

    ```bash
    # Port forward to access service
    kubectl port-forward svc/messaging-app-service 8000:8000

    # Access in browser: http://localhost:8000

    # Check application logs
    kubectl logs -f deployment/messaging-app -c messaging-app
    ```

6. Verify Functionality

    ```bash
    # Check health endpoint
    curl http://localhost:8000/api/v1/health/

    # Check running pods
    kubectl get pods

    # Check service status
    kubectl get svc

    # View Kubernetes dashboard
    minikube dashboard
    ```

7. Test Scaling

    ```bash
    # Scale deployment
    kubectl scale deployment messaging-app --replicas=3

    # Verify pod distribution
    kubectl get pods -o wide
    ```

8. Perform Rolling Update

    ```bash
    # Update to new version
    kubectl set image deployment/messaging-app messaging-app=<your-dockerhub-username>/messaging-app:1.1.0

    # Monitor rollout status
    kubectl rollout status deployment/messaging-app
    ```

9. Cleanup

    ```bash
    # Delete deployment
    kubectl delete -f deployment.yaml
    kubectl delete -f db-deployment.yaml

    # Stop Minikube
    minikube stop

    # Delete cluster
    minikube delete
    ```

### Key Components

- Deployment: 2 replicas with rolling updates
- Service: ClusterIP for internal access
- ConfigMap: Non-sensitive configuration
- Secret: Sensitive credentials (use proper management in production)
- Database: PostgreSQL with persistent storage
- Health Checks: Liveness and readiness probes

---

## Kubernetes Deployment Guide

### Prerequisites

- Kubernetes cluster (Minikube, Docker Desktop, or cloud provider)
- `kubectl` command-line tool
- Docker image of the application pushed to a container registry
- `envsubst` utility (usually comes with `gettext` package)

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_NAME=messaging_db
DB_USER=messaging_user
DB_PASSWORD=your_secure_password
POSTGRES_PASSWORD=your_secure_password

# Django Settings
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=*

# Database URL (auto-generated)
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
```

### Deployment Steps

1. **Create Kubernetes Secrets**

   ```bash
   # Create namespace
   kubectl create namespace messaging
   
   # Create secrets from .env file
   kubectl create secret generic messaging-app-secrets \
     --from-env-file=.env \
     --namespace=messaging
   ```

2. **Apply Database Configuration**

   ```bash
   # Create persistent volumes and claims
   kubectl apply -f k8s/db-storage.yaml -n messaging
   
   # Deploy PostgreSQL
   kubectl apply -f k8s/db-deployment.yaml -n messaging
   ```

3. **Deploy the Application**

   ```bash
   # Apply the deployment
   kubectl apply -f k8s/deployment.yaml -n messaging
   
   # Verify the deployment
   kubectl get pods -n messaging
   ```

4. **Access the Application**

   ```bash
   # Port-forward to access the service
   kubectl port-forward svc/messaging-app-service 8000:8000 -n messaging
   ```

   The application will be available at: <http://localhost:8000>

### Monitoring and Logs

```bash
# View application logs
kubectl logs -l app=messaging-app -n messaging --tail=50 -f

# Monitor resource usage
kubectl top pods -n messaging

# Check pod status
kubectl get pods -n messaging

# View service details
kubectl describe svc messaging-app-service -n messaging
```

### Scaling the Application

```bash
# Scale up
kubectl scale deployment messaging-app --replicas=3 -n messaging

# Scale down
kubectl scale deployment messaging-app --replicas=1 -n messaging
```

### Database Management

#### Run Migrations

```bash
kubectl exec -it $(kubectl get pods -n messaging -l app=messaging-app -o jsonpath='{.items[0].metadata.name}') -n messaging -- python manage.py migrate
```

#### Create Superuser

```bash
kubectl exec -it $(kubectl get pods -n messaging -l app=messaging-app -o jsonpath='{.items[0].metadata.name}') -n messaging -- python manage.py createsuperuser
```

### Backup and Restore

#### Regular Backups

```bash
# Create a daily backup job
kubectl create cronjob --image=postgres:14 --scheme="0 0 * * *" -- \
  /bin/sh -c "PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h postgres -U $POSTGRES_USER $DB_NAME | gzip > /backup/db-$(date +%Y%m%d).sql.gz"
```

#### Restore from Backup

```bash
# Find the backup file
kubectl exec -it <postgres-pod> -- ls -la /backup/

# Restore the database
kubectl exec -i <postgres-pod> -- gunzip -c /backup/db-20230812.sql.gz | \
  kubectl exec -i <postgres-pod> -- psql -U $POSTGRES_USER $DB_NAME
```

### Performance Tuning

#### Database Tuning

- Adjust PostgreSQL configuration in the StatefulSet
- Configure connection pooling (e.g., PgBouncer)
- Add read replicas for read-heavy workloads

#### Application Tuning

- Configure Django's cache backend
- Use a CDN for static files
- Enable GZIP compression
- Optimize database queries

### Security Hardening

1. **Network Policies**
   - Restrict ingress/egress traffic
   - Only allow necessary ports and protocols

2. **Pod Security Policies**
   - Enable Pod Security Admission
   - Restrict privileged containers
   - Enforce read-only root filesystem

3. **RBAC**
   - Use minimal required permissions
   - Create dedicated service accounts
   - Avoid using cluster-admin

### Scaling the Infrastructure

#### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: messaging-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: messaging-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### Cluster Autoscaler

- Configure your cluster autoscaler to automatically add nodes when needed
- Set appropriate resource requests and limits
- Use node selectors and taints for workload placement

### Security Considerations

1. **Secrets Management**
   - Never commit `.env` files to version control
   - Use Kubernetes secrets or external secret management systems
   - Rotate secrets regularly

2. **Network Security**
   - Network policies restrict traffic between pods
   - Use internal services (ClusterIP) for internal communication
   - Expose only necessary ports

3. **Pod Security**
   - Run containers as non-root users
   - Use read-only root filesystem where possible
   - Drop all capabilities not explicitly required

### Monitoring and Alerting

#### Prometheus Metrics

Metrics are exposed on the `/metrics` endpoint. To set up monitoring:

1. Install Prometheus and Grafana
2. Configure Prometheus to scrape the metrics endpoint
3. Import the Django dashboard for Grafana

#### Logging

Logs are sent to stdout and can be collected using a log aggregation system like:

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd
- Loki with Grafana

### High Availability

- The application is deployed with multiple replicas
- Pod anti-affinity ensures pods are scheduled on different nodes
- Database persistence ensures data survives pod restarts
- Liveness and readiness probes ensure traffic is only sent to healthy pods

### Backup and Disaster Recovery

#### Regular Backups

```bash
# Create a daily backup job
kubectl create cronjob --image=postgres:14 --scheme="0 0 * * *" -- \
  /bin/sh -c "PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h postgres -U $POSTGRES_USER $DB_NAME | gzip > /backup/db-$(date +%Y%m%d).sql.gz"
```

#### Restore from Backup

```bash
# Find the backup file
kubectl exec -it <postgres-pod> -- ls -la /backup/

# Restore the database
kubectl exec -i <postgres-pod> -- gunzip -c /backup/db-20230812.sql.gz | \
  kubectl exec -i <postgres-pod> -- psql -U $POSTGRES_USER $DB_NAME
```

---

## Manual Setup (Alternative)

If you prefer to set up the development environment manually:

### Prerequisites (Python)

- Python 3.12+
- PostgreSQL 17+
- pip (Python package installer)

### Installation Steps

1. **Create a virtual environment**:

    ```bash
    python -m venv .venv
    ```

2. **Activate the environment**:

    ```bash
    source .venv/scripts/activate  # Windows
    source .venv/bin/activate     # MacOS/Linux
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up PostgreSQL database** and create a database named `messaging_app_db`

5. **Environment Configuration**:

    ```bash
    cp .env.docker .env
    # Edit .env file with your database credentials
    ```

6. **Apply migrations**:

    ```bash
    python manage.py migrate
    ```

7. **Create test data**:

    ```bash
    python manage.py create_test_data
    ```

8. **Create admin user**:

    ```bash
    python manage.py createsuperuser
    ```

9. **Start development server**:

    ```bash
    python manage.py runserver
    ```

## MySQL Setup Instructions

### Prerequisites (MySQL)

- MySQL Server installed ([Installation Guide](https://dev.mysql.com/doc/refman/8.0/en/installing.html))
- MySQL Client installed ([Installation Guide](https://dev.mysql.com/doc/refman/8.0/en/installing.html))

### Setup Instructions (MySQL)

1. **Create a new MySQL database**:

    ```sql
    CREATE DATABASE messaging_app;
    ```

2. **Create a new MySQL user**:

    ```sql
    CREATE USER 'messaging_user'@'%' IDENTIFIED BY 'your-secure-password';
    ```

3. **Grant privileges to the new user**:

    ```sql
    GRANT ALL PRIVILEGES ON messaging_app.* TO 'messaging_user'@'%';
    ```

4. **Apply database migrations**:

    ```bash
    python manage.py migrate
    ```

5. **Create test data**:

    ```bash
    python manage.py create_test_data
    ```

6. **Create admin user**:

    ```bash
    python manage.py createsuperuser
    ```

7. **Start development server**:

    ```bash
    python manage.py runserver
    ```

## Environment Configuration

### Docker Environment (.env.docker)

For Docker setup, use the provided `.env.docker` template:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_NAME=messaging_app_db
DB_USER=messaging_user
DB_PASSWORD=messaging_pass
DB_HOST=db
DB_PORT=5432
```

### Local Development Environment

For manual setup, create `.env` file:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=your_local_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

## Dependencies

- Django 5.2.4+
- Django REST Framework 3.16.0+
- djangorestframework-simplejwt (JWT Authentication)
- django-environ (for environment variables)
- django-filter (for API filtering)
- psycopg (PostgreSQL adapter)
- python-dateutil (for date handling)
- mysqlclient (MySQL adapter)

## Project Structure

```text
messaging_app/
├── .venv/                 # Virtual environment
├── chats/                 # Messaging app
│   ├── migrations/        # Database migrations
│   ├── management/        # Custom management commands
│   ├── __init__.py
│   ├── admin.py           # Admin panel config
│   ├── apps.py
│   ├── models.py          # Data models
│   ├── permissions.py     # Custom permissions
│   ├── serializers.py     # API serializers
│   ├── urls.py            # API endpoints
│   └── views.py           # View logic
├── messaging_app/         # Project config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py
├── .env.docker            # Docker environment template
├── .dockerignore          # Docker ignore file
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── entrypoint.sh          # Docker entrypoint script
├── .gitignore
├── manage.py
├── README.md              # Project documentation
└── requirements.txt       # Dependencies file
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

- **IsAuthenticated**: Required for all API endpoints
- **IsParticipantOfConversation**: Users must be participants to view/modify conversations
- **IsMessageOwnerOrReadOnly**: Only message owners can edit/delete their messages
- **IsAdminUser**: Required for admin interface access

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

- Returns 20 messages per page by default
- Use `page` parameter to navigate through pages
- Customize page size with `page_size` parameter (max 100)

**Filtering**:

- `sender`: Filter by sender ID or username
- `start_date`: Filter messages sent after this date (YYYY-MM-DD HH:MM:SS)
- `end_date`: Filter messages sent before this date (YYYY-MM-DD HH:MM:SS)
- `search`: Search in message content (case-insensitive)

**Sorting**:

- Use `ordering` parameter with:
  - `sent_at` (ascending)
  - `-sent_at` (descending, default)
  - `sender__username` (alphabetical by sender)
  - `-sender__username` (reverse alphabetical by sender)

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

## Testing the API

### Docker Environment

With Docker running, you can test the API:

```bash
# Get token for test user 'kwame'
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kwame", "password": "testpass123"}'

# Use the returned token to access protected endpoints
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/conversations/
```

### Test Data

Pre-created test users (available after running `create_test_data` command):

1. **Kwame Mensah**
   - Username: `kwame`
   - Password: `testpass123`

2. **Ama Agyei**
   - Username: `ama`
   - Password: `testpass123`

3. **Kofi Asante**
   - Username: `kofi`
   - Password: `testpass123`

**Note**: Kwame and Ama share a conversation with test messages in Twi.

## Testing Permissions

### 1. Unauthenticated Access (401)

```bash
curl -X GET http://localhost:8000/api/v1/conversations/
# Should return 401 Unauthorized
```

### 2. Non-Participant Access (403)

```bash
# Get Kofi's token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "kofi", "password": "testpass123"}' | jq -r '.access')

# Try to access Kwame and Ama's conversation
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/conversations/1/
# Should return 403 Forbidden
```

## Admin Interface

Access the admin interface at `http://localhost:8000/admin/` using admin credentials.

### Default Admin Credentials (Docker)

- **Username**: `admin`
- **Password**: `admin123`

### Admin Features

- User management (create, edit, delete users)
- View all conversations
- Monitor messages
- User role management

## Development

### Creating Migrations

```bash
# In Docker environment
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# In manual setup
python manage.py makemigrations
python manage.py migrate
```

### Running Tests

```bash
# In Docker environment
docker-compose exec web python manage.py test

# In manual setup
python manage.py test
```

### Accessing Django Shell

```bash
# In Docker environment
docker-compose exec web python manage.py shell

# In manual setup
python manage.py shell
```

## Production Deployment

### Docker Production Setup

1. **Create production Docker Compose file** (`docker-compose.prod.yml`):
   - Use production-ready PostgreSQL configuration
   - Set proper environment variables
   - Configure nginx for static file serving
   - Use gunicorn instead of development server

2. **Security Considerations**:
   - Use secure `SECRET_KEY`
   - Set `DEBUG=False`
   - Configure proper `ALLOWED_HOSTS`
   - Use SSL/TLS certificates
   - Implement proper backup strategies

3. **Environment Variables**:
   - Use Docker secrets or external secret management
   - Never commit production credentials to version control

## Troubleshooting

### Common Docker Issues

1. **Port Already in Use**:

   ```bash
   # Change port in docker-compose.yml or stop conflicting service
   docker-compose down
   sudo lsof -i :8000  # Find what's using port 8000
   ```

2. **Database Connection Issues**:

   ```bash
   # Check if PostgreSQL container is running
   docker-compose logs db
   # Restart services
   docker-compose restart
   ```

3. **Permission Issues**:

   ```bash
   # Fix file permissions (Linux/macOS)
   sudo chown -R $USER:$USER .
   ```

4. **Container Build Issues**:

   ```bash
   # Clear Docker cache and rebuild
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

### Common Development Issues

1. **Migration Issues**:

   ```bash
   # Reset migrations (development only)
   docker-compose exec web python manage.py migrate --fake-initial
   ```

2. **Static Files Not Loading**:

   ```bash
   # Collect static files
   docker-compose exec web python manage.py collectstatic
   ```

## Security Considerations

- Always use HTTPS in production
- Tokens expire after 1 hour (configurable in settings)
- Refresh tokens expire after 1 day
- Passwords are hashed before storage
- Admin interface is protected by `IsAdminUser`
- Rate limiting recommended for authentication endpoints
- Use proper secrets management in production
- Regular security audits and dependency updates

## Performance Optimization

- Database query optimization with `select_related`/`prefetch_related`
- Implement Redis caching for production
- Use CDN for static file delivery
- Database connection pooling
- Implement API rate limiting
- Monitor with APM tools (Sentry, New Relic)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the ALX ProDEV Curriculum.
