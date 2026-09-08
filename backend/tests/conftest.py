import os

os.environ["NOCFLOW_ENVIRONMENT"] = "test"
os.environ["NOCFLOW_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["NOCFLOW_CORS_ORIGINS"] = '["http://localhost:4200"]'
