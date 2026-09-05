import sqlite3
import json
import os
from typing import List, Optional, Dict, Any

if os.getenv("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DB_PATH = "/tmp/truelens.db"
else:
    try:
        test_file = os.path.join(os.path.dirname(__file__), ".write_test")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        DB_PATH = os.path.join(os.path.dirname(__file__), "truelens.db")
    except Exception:
        DB_PATH = "/tmp/truelens.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database tables and schema migrations if needed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id TEXT PRIMARY KEY,
            media_type TEXT NOT NULL DEFAULT 'image',
            timestamp TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            format TEXT NOT NULL,
            verdict TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            confidence INTEGER NOT NULL,
            result_json TEXT NOT NULL
        )
        """
    )
    
    cursor.execute("PRAGMA table_info(analysis_history)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "media_type" not in columns:
        cursor.execute("ALTER TABLE analysis_history ADD COLUMN media_type TEXT NOT NULL DEFAULT 'image'")
        
    conn.commit()
    conn.close()

# Ensure table exists on module load
init_db()


def save_analysis(result_data: Dict[str, Any]) -> None:
    """Saves a completed image, audio, or video analysis result to SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    media_type = result_data.get("media_type", "image")
    confidence = result_data.get("confidence") or result_data.get("assessment_confidence", 90)

    cursor.execute(
        """
        INSERT OR REPLACE INTO analysis_history 
        (id, media_type, timestamp, filename, file_size, format, verdict, risk_score, confidence, result_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result_data["analysis_id"],
            media_type,
            result_data["timestamp"],
            result_data["filename"],
            result_data["file_size"],
            result_data["format"],
            result_data["verdict"],
            result_data["risk_score"],
            confidence,
            json.dumps(result_data),
        ),
    )
    conn.commit()
    conn.close()


def get_all_analyses(limit: int = 30, offset: int = 0, media_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches analysis history list, optionally filtered by media_type ('image' / 'audio' / 'video')."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if media_type:
        cursor.execute(
            """
            SELECT id, media_type, timestamp, filename, file_size, format, verdict, risk_score, confidence
            FROM analysis_history
            WHERE media_type = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (media_type, limit, offset),
        )
    else:
        cursor.execute(
            """
            SELECT id, media_type, timestamp, filename, file_size, format, verdict, risk_score, confidence
            FROM analysis_history
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full analysis detail by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT result_json FROM analysis_history WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["result_json"])
    return None


def delete_analysis_by_id(analysis_id: str) -> bool:
    """Deletes analysis record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history WHERE id = ?", (analysis_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
