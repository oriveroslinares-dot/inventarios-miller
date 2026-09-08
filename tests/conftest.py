import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_tmpdir = tempfile.mkdtemp(prefix="triple_aaa_tests_")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ["UPLOAD_DIR"] = os.path.join(_tmpdir, "uploads")
os.environ["LOAD_DEMO_DATA"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.makedirs(os.environ["UPLOAD_DIR"], exist_ok=True)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base


@pytest.fixture()
def db_session():
    """Sesión de base de datos SQLite en memoria, aislada por prueba, para
    ejercitar la capa de servicios sin depender del ciclo de vida de la app."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    """Cliente de pruebas contra la aplicación completa (API + panel + portal),
    respaldado por un archivo SQLite temporal compartido durante la sesión de pruebas."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c
