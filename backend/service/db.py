"""SQLite 档案存储（纯标准库 sqlite3，零 ORM 依赖，简单可靠）。"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config


def _conn() -> sqlite3.Connection:
    p = config.DATABASE_PATH
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT,
                breed TEXT,
                body_condition TEXT,
                coat_condition TEXT,
                health_notes TEXT,
                confidence REAL,
                image_data_url TEXT,
                mode TEXT,
                created_at TEXT
            )
            """
        )


def create_pet(record: Dict) -> int:
    with _conn() as c:
        cur = c.execute(
            """
            INSERT INTO pets
              (name, species, breed, body_condition, coat_condition, health_notes,
               confidence, image_data_url, mode, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (
                record.get("name", "未命名"),
                record.get("species"),
                record.get("breed"),
                record.get("body_condition"),
                record.get("coat_condition"),
                record.get("health_notes"),
                record.get("confidence", 0.0),
                record.get("image_data_url"),
                record.get("mode"),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return cur.lastrowid


def list_pets() -> List[Dict]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM pets ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def get_pet(pet_id: int) -> Optional[Dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM pets WHERE id=?", (pet_id,)).fetchone()
        return dict(row) if row else None


def delete_pet(pet_id: int) -> bool:
    """删除指定档案，返回是否成功删除了记录。"""
    with _conn() as c:
        cur = c.execute("DELETE FROM pets WHERE id=?", (pet_id,))
        return cur.rowcount > 0


def export_json() -> List[Dict]:
    """轻量导出全部档案为 JSON。"""
    return [{"id": p["id"], "name": p["name"], "species": p["species"],
             "breed": p["breed"], "body_condition": p["body_condition"],
             "coat_condition": p["coat_condition"], "health_notes": p["health_notes"],
             "confidence": p["confidence"], "mode": p["mode"], "created_at": p["created_at"]}
            for p in list_pets()]
