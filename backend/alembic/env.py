"""Alembic env — usa la configuración del proyecto Neovate."""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Permitir `from backend.* import ...` cuando alembic corre desde /backend
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.config import settings  # noqa: E402
from backend.core.database import Base  # noqa: E402
from backend import models  # noqa: F401,E402  — registra tablas en Base.metadata


config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine, text
    # statement_timeout=20s evita que la migración bloquee la DB para siempre
    url = settings.database_url + ("&" if "?" in settings.database_url else "?") + "connect_timeout=10"
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args={"options": "-c statement_timeout=20000 -c lock_timeout=10000"},
    )
    with connectable.connect() as connection:
        connection.execute(text("SET statement_timeout = '20s'"))
        connection.execute(text("SET lock_timeout = '10s'"))
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
