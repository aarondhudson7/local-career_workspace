import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_PATH = "job_cache.db"

def get_url_hash(url: str) -> str:
    """Generate a unique string token from the URL to map data keys cleanly."""
    return hashlib.md5(url.strip().encode("utf-8")).hexdigest()

def init_cache_db():
    """Create the local SQLite layout schema automatically if missing."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_listings (
                url_hash TEXT PRIMARY KEY,
                url TEXT,
                job_text TEXT,
                cached_at TEXT
            )
        """)
        conn.commit()

def get_cached_job(url: str, max_days: int = 7) -> str:
    """
    Retrieve job description text if it exists and is fresher than max_days.
    Returns None if cache is expired or missing.
    """
    init_cache_db()
    url_hash = get_url_hash(url)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT job_text, cached_at FROM job_listings WHERE url_hash = ?", 
            (url_hash,)
        )
        row = cursor.fetchone()
        
    if not row:
        return None
        
    job_text, cached_at_str = row
    cached_at = datetime.fromisoformat(cached_at_str)
    
    # Check if the data age exceeds the day threshold expiration limit
    if datetime.now() - cached_at > timedelta(days=max_days):
        return None  # Triggers a fresh browser scrape loop
        
    return job_text

def save_job_to_cache(url: str, job_text: str):
    """Insert or update a job payload with a current timestamp footprint."""
    init_cache_db()
    url_hash = get_url_hash(url)
    now_str = datetime.now().isoformat()
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO job_listings (url_hash, url, job_text, cached_at)
            VALUES (?, ?, ?, ?)
        """, (url_hash, url.strip(), job_text, now_str))
        conn.commit()

