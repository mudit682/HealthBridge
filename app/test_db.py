from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL is not set in the environment variables.")
else:
    # Try to create the engine and connect to the database
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Successfully connected to the database!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
