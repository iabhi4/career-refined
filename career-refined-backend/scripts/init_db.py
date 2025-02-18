import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.settings import settings
from config.database import Base, engine
# Import all models to ensure they're registered with SQLAlchemy
from schemas import User, WorkExperience, Education, Project, Application, Auth, ApplicationAnalysis

def create_database():
    """Create database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (to postgres database)
        conn = psycopg2.connect(
            dbname="postgres",
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{settings.DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
            print(f"Database '{settings.DB_NAME}' created successfully!")
        else:
            print(f"Database '{settings.DB_NAME}' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

def create_tables():
    """Create all tables in the database."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Successfully created all tables!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def init_db():
    """Initialize database and create all tables."""
    print("Starting database initialization...")
    create_database()
    create_tables()
    print("Database initialization completed!")

if __name__ == "__main__":
    init_db()