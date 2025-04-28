notepad app\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Fill in your MySQL credentials here:
DB_USER = "root"          # or "root"
DB_PASSWORD = "Pyro2002"    # your password
DB_HOST = "localhost"
DB_NAME = "immunization_tracker"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# SQLAlchemy engine & session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



