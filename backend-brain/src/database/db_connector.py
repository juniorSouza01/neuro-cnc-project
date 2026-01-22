import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import Config

def get_connection():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASS
    )
    return conn

def save_telemetry(data: dict):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO telemetry (time, spindle_load, spindle_temp)
            VALUES (%s, %s, %s)
        """
        cur.execute(query, (data['timestamp'], data['spindle_load'], data['temp']))
        conn.commit()
    finally:
        conn.close()

def get_recent_telemetry(limit=100):
    """Busca os últimos N pontos para alimentar a IA"""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM telemetry ORDER BY time DESC LIMIT %s", (limit,))
        return cur.fetchall()
    finally:
        conn.close()