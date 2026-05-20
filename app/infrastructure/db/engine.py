from collections.abc import Iterator

from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///db/development.sqlite3"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
