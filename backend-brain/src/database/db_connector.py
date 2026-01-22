import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import Config


def save_action(part_id, suggested_val):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO ai_actions (run_id, suggested_offset_vc, confidence_score)
            VALUES (%s, %s, 0.95) RETURNING id
        """
        run_id = abs(hash(part_id)) % 10000 
        cur.execute(query, (run_id, suggested_val))
        id = cur.fetchone()[0]
        conn.commit()
        return id
    finally:
        conn.close()
        
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