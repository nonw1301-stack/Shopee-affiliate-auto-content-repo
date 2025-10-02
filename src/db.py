import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data.db"

class DB:
    def __init__(self, path=DB_PATH):
        self.path = path
        self.conn = sqlite3.connect(str(self.path))
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS posted_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL UNIQUE,
            shop_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def is_posted(self, item_id):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM posted_items WHERE item_id = ?", (item_id,))
        return cur.fetchone() is not None

    def mark_posted(self, item_id, shop_id=None):
        cur = self.conn.cursor()
        try:
            cur.execute("INSERT INTO posted_items (item_id, shop_id) VALUES (?, ?)", (item_id, shop_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self):
        self.conn.close()
