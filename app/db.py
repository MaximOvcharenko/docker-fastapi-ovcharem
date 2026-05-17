import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://devuser:devpassword@localhost:5432/devdb")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True, index=True)

    todos = relationship("ToDo", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    todos = relationship("ToDo", back_populates="category")

class ToDo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    text = Column(Text, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="todos")
    category = relationship("Category", back_populates="todos")


def init_db():
    import time
    from sqlalchemy.exc import OperationalError
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            Base.metadata.create_all(bind=engine)
            print("✓ Database initialized successfully")
            return
        except OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"✗ Failed to connect to database after {max_retries} retries")
                raise
            print(f"⏳ Database not ready yet, retrying... ({retry_count}/{max_retries})")
            time.sleep(1)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_default_data():
    from sqlalchemy import select
    import time
    from sqlalchemy.exc import OperationalError
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with SessionLocal() as db:
                categories = db.execute(select(Category)).scalars().all()
                if not categories:
                    default_names = ["Work", "Home", "Shopping", "Other"]
                    db.add_all([Category(name=name) for name in default_names])
                    db.commit()
                    print("✓ Categories created")

                users = db.execute(select(User)).scalars().all()
                if not users:
                    demo_user = User(username="demo_user", api_key="demo-key-12345")
                    db.add(demo_user)
                    db.commit()
                    print("✓ Demo user created")
            return
        except OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"⚠ Failed to create default data after {max_retries} retries")
                return
            print(f"⏳ Retrying default data creation... ({retry_count}/{max_retries})")
            time.sleep(1)
