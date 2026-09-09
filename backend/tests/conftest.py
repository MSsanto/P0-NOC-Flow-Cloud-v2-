import os

# Respect explicit CI/integration environment configuration. Local test runs fall
# back to an isolated in-memory SQLite database for unit tests.
os.environ.setdefault("NOCFLOW_ENVIRONMENT", "test")
os.environ.setdefault("NOCFLOW_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("NOCFLOW_CORS_ORIGINS", '["http://localhost:4200"]')
