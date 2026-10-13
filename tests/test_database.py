from app.database import Base
from app import models


def test_database_models_are_registered():
    assert len(Base.metadata.tables) >= 18


def test_required_tables_exist():
    tables = set(Base.metadata.tables.keys())

    assert "users" in tables
    assert "doctors" in tables
    assert "appointments" in tables
    assert "consultations" in tables
    assert "audit_logs" in tables
