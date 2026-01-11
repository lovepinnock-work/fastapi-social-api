## About This Project
This project is a backend API for a social media application.

It is built using **FastAPI** for request handling, **Pydantic** for schema and response validation, and **SQLAlchemy** for persistence to a **PostgreSQL** database. Database schema changes are managed with **Alembic** migrations. Alembic migrations are linear, reversible, and align with SQLAlchemy models. CI validates migrations against a clean Postgres instance before running tests.

The application includes full test coverage using **pytest**, as well as smoke and stress testing using **k6** to validate behavior under load.

SwaggerUI and ReDoc are provided for interactive API documentation.

---

## Features
- User registration and authentication using OAuth2 password flow
- JWT-based authorization for protected routes
- CRUD operations for posts
- Voting system (like / unlike posts)
- Rate limiting on authentication attempts
- Comprehensive unit and integration tests
- Load and stress testing with documented performance metrics

---

## Running the Application Locally
Application available at: http://localhost:8000/
Swagger docs: http://localhost:8000/docs
```bash
docker compose -f docker-compose-dev.yml up --build
```

## Testing

Tests are written using pytest and located in the /tests directory.
They cover:
- Core CRUD functionality
- Authentication and authorization flows
- Edge cases and invalid input handling
Run tests with:
```bash
pytest
```

## Performance Testing
Smoke and stress testing were performed using k6 to evaluate system behavior under normal and high concurrency. Details, results and further analysis found in /docs/README.md

