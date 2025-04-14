# db_connection.py
from sqlalchemy import create_engine

def get_engine():
    DB_URL = "postgresql://postgres:gharm@localhost:5432/chess_data"
    engine = create_engine(DB_URL)
    return engine
