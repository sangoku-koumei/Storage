"""
データベース接続とセッション管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# SQLiteの場合はcheck_same_thread=Falseが必要
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,  # DEBUGモードでSQLをログ出力
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI用のDBセッション依存性"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


