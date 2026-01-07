# Email Workflow Engine

A Python-based email workflow engine with state machine processing, automatic email classification, and deadline-based transitions.

## Features

- **State Machine Workflows**: Define workflows with states, events, transitions, and conditions
- **Email Classification**: Keyword-based or LLM-based email content classification
- **Background Processing**: Celery-based task processing for emails and deadlines
- **REST API**: FastAPI-powered API with JWT authentication
- **Admin Interface**: Web-based admin panel for monitoring and management
- **AWS SES Integration**: Send and receive emails via AWS SES

## Tech Stack

- Python 3.13+
- FastAPI
- PostgreSQL with SQLAlchemy (async)
- Celery with Redis
- AWS SES
- Alembic for migrations

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+

### Development Setup

1. Clone the repository and navigate to the project:
   ```bash
   cd workflow-engine
   ```

2. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start the services:
   ```bash
   make build
   make up
   ```

4. Run database migrations:
   ```bash
   make migrate
   ```

5. Access the services:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Admin: http://localhost:8000/admin
   - Mailhog (email testing): http://localhost:8025

### Local Development (without Docker)

1. Install dependencies:
   ```bash
   make install
   ```

2. Start PostgreSQL and Redis locally

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the API:
   ```bash
   uvicorn workflow_engine.main:app --reload
   ```

5. Start the Celery worker:
   ```bash
   celery -A workflow_engine.worker.celery_app worker --loglevel=info
   ```

## Project Structure

```
workflow-engine/
├── src/workflow_engine/
│   ├── api/              # FastAPI application
│   ├── admin/            # Admin web interface
│   ├── db/               # Database models and repositories
│   ├── email/            # Email utilities (AWS SES)
│   ├── worker/           # Celery background tasks
│   └── workflows/        # State machine framework
├── alembic/              # Database migrations
├── docker/               # Docker configuration
├── tests/                # Unit tests
└── Makefile              # Common commands
```

## Creating a Workflow

1. Create a new directory under `src/workflow_engine/workflows/types/`:
   ```
   workflows/types/my_workflow/
   ├── __init__.py
   ├── events.py
   ├── state_machine.py
   └── classifier.py
   ```

2. Define your events:
   ```python
   from workflow_engine.workflows.base.event import BaseEventType

   class MyEventType(BaseEventType):
       REQUEST_RECEIVED = "REQUEST_RECEIVED"
       APPROVED = "APPROVED"
       REJECTED = "REJECTED"
   ```

3. Create your state machine:
   ```python
   from workflow_engine.workflows.base.state_machine import AbstractStateMachine
   from workflow_engine.workflows.base.transition import Transition

   class MyStateMachine(AbstractStateMachine[MyEventType]):
       @property
       def initial_state(self) -> str:
           return "pending"

       def get_transitions(self) -> list[Transition[MyEventType]]:
           return [
               Transition(
                   from_state="pending",
                   event=MyEventType.REQUEST_RECEIVED,
                   to_state="processing",
               ),
               # ... more transitions
           ]
   ```

4. Register your workflow:
   ```python
   from workflow_engine.workflows.registry import WorkflowRegistry, WorkflowDefinition

   WorkflowRegistry.register(WorkflowDefinition(
       name="MY_WORKFLOW",
       state_machine_class=MyStateMachine,
       classifier=MyClassifier(),
   ))
   ```

## API Authentication

The API uses JWT tokens. To authenticate:

1. Get a token:
   ```bash
   curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your-password"}'
   ```

2. Use the token in requests:
   ```bash
   curl http://localhost:8000/api/v1/requests \
     -H "Authorization: Bearer <your-token>"
   ```

## Configuration

All configuration is done via environment variables. See `.env.example` for available options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `AWS_*`: AWS credentials for SES
- `ADMIN_*`: Admin interface credentials

## Testing

Run the test suite:
```bash
make test
```

Or locally:
```bash
make test-local
```

## License

MIT
