"""Flotion backend — a deliberately small Notion clone API.

FastAPI + the stdlib `sqlite3` module (no ORM). Two tables, `pages` and
`blocks`, give us a sidebar of pages where each page is an ordered list of
editable text blocks. This is the *working baseline*; the agent team extends
it (nested pages, block types, search, …) on top of these endpoints.

Run:  uv run uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "flotion.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL DEFAULT 'Untitled',
    parent_id  INTEGER REFERENCES pages(id) ON DELETE CASCADE,
    position   INTEGER NOT NULL DEFAULT 0,
    created_at REAL    NOT NULL,
    updated_at REAL    NOT NULL
);
CREATE TABLE IF NOT EXISTS blocks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id    INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    type       TEXT    NOT NULL DEFAULT 'text',
    content    TEXT    NOT NULL DEFAULT '',
    position   INTEGER NOT NULL DEFAULT 0,
    created_at REAL    NOT NULL,
    updated_at REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_blocks_page ON blocks(page_id, position);
"""


def now() -> float:
    return time.time()


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) AS n FROM pages").fetchone()["n"]
        if count == 0:
            ts = now()
            cur = conn.execute(
                "INSERT INTO pages (title, parent_id, position, created_at, updated_at) "
                "VALUES (?, NULL, 0, ?, ?)",
                ("Welcome to Flotion", ts, ts),
            )
            page_id = cur.lastrowid
            seed_blocks = [
                ("heading", "Flotion"),
                ("text", "A tiny Notion clone — Vue 3 + FastAPI + SQLite."),
                ("text", "Click a page in the sidebar, edit its title, and add blocks below."),
                ("text", "Press Enter at the end of a block to create the next one."),
            ]
            for pos, (btype, content) in enumerate(seed_blocks):
                conn.execute(
                    "INSERT INTO blocks (page_id, type, content, position, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (page_id, btype, content, pos, ts, ts),
                )


# ── Schemas ────────────────────────────────────────────────────────────────
class PageCreate(BaseModel):
    title: str = "Untitled"
    parent_id: Optional[int] = None


class PageUpdate(BaseModel):
    title: Optional[str] = None
    parent_id: Optional[int] = None
    position: Optional[int] = None


class BlockCreate(BaseModel):
    type: str = "text"
    content: str = ""
    position: Optional[int] = None


class BlockUpdate(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    position: Optional[int] = None


# ── App ──────────────────────────────────────────────────────────────────--
app = FastAPI(title="Flotion API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


@app.get("/api/health")
def health():
    return {"ok": True, "service": "flotion", "version": "0.1.0"}


# ── Pages ────────────────────────────────────────────────────────────────--
@app.get("/api/pages")
def list_pages():
    with db() as conn:
        rows = conn.execute(
            "SELECT id, title, parent_id, position FROM pages "
            "ORDER BY position, id"
        ).fetchall()
    return [row_to_dict(r) for r in rows]


@app.post("/api/pages", status_code=201)
def create_page(body: PageCreate):
    ts = now()
    with db() as conn:
        pos = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 AS p FROM pages").fetchone()["p"]
        cur = conn.execute(
            "INSERT INTO pages (title, parent_id, position, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (body.title or "Untitled", body.parent_id, pos, ts, ts),
        )
        row = conn.execute("SELECT * FROM pages WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.get("/api/pages/{page_id}")
def get_page(page_id: int):
    with db() as conn:
        page = conn.execute("SELECT * FROM pages WHERE id = ?", (page_id,)).fetchone()
        if page is None:
            raise HTTPException(404, "page not found")
        blocks = conn.execute(
            "SELECT * FROM blocks WHERE page_id = ? ORDER BY position, id", (page_id,)
        ).fetchall()
    data = row_to_dict(page)
    data["blocks"] = [row_to_dict(b) for b in blocks]
    data["word_count"] = sum(len(b["content"].split()) for b in data["blocks"])
    return data


@app.patch("/api/pages/{page_id}")
def update_page(page_id: int, body: PageUpdate):
    fields = body.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(400, "no fields to update")
    fields["updated_at"] = now()
    sets = ", ".join(f"{k} = ?" for k in fields)
    with db() as conn:
        if conn.execute("SELECT 1 FROM pages WHERE id = ?", (page_id,)).fetchone() is None:
            raise HTTPException(404, "page not found")
        conn.execute(f"UPDATE pages SET {sets} WHERE id = ?", (*fields.values(), page_id))
        row = conn.execute("SELECT * FROM pages WHERE id = ?", (page_id,)).fetchone()
    return row_to_dict(row)


@app.delete("/api/pages/{page_id}", status_code=204)
def delete_page(page_id: int):
    with db() as conn:
        if conn.execute("SELECT 1 FROM pages WHERE id = ?", (page_id,)).fetchone() is None:
            raise HTTPException(404, "page not found")
        conn.execute("DELETE FROM pages WHERE id = ?", (page_id,))
    return None


# ── Blocks ───────────────────────────────────────────────────────────────--
@app.post("/api/pages/{page_id}/blocks", status_code=201)
def create_block(page_id: int, body: BlockCreate):
    ts = now()
    with db() as conn:
        if conn.execute("SELECT 1 FROM pages WHERE id = ?", (page_id,)).fetchone() is None:
            raise HTTPException(404, "page not found")
        if body.position is None:
            pos = conn.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 AS p FROM blocks WHERE page_id = ?",
                (page_id,),
            ).fetchone()["p"]
        else:
            pos = body.position
            conn.execute(
                "UPDATE blocks SET position = position + 1 WHERE page_id = ? AND position >= ?",
                (page_id, pos),
            )
        cur = conn.execute(
            "INSERT INTO blocks (page_id, type, content, position, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (page_id, body.type, body.content, pos, ts, ts),
        )
        row = conn.execute("SELECT * FROM blocks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.patch("/api/blocks/{block_id}")
def update_block(block_id: int, body: BlockUpdate):
    fields = body.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(400, "no fields to update")
    fields["updated_at"] = now()
    sets = ", ".join(f"{k} = ?" for k in fields)
    with db() as conn:
        if conn.execute("SELECT 1 FROM blocks WHERE id = ?", (block_id,)).fetchone() is None:
            raise HTTPException(404, "block not found")
        conn.execute(f"UPDATE blocks SET {sets} WHERE id = ?", (*fields.values(), block_id))
        row = conn.execute("SELECT * FROM blocks WHERE id = ?", (block_id,)).fetchone()
    return row_to_dict(row)


@app.delete("/api/blocks/{block_id}", status_code=204)
def delete_block(block_id: int):
    with db() as conn:
        if conn.execute("SELECT 1 FROM blocks WHERE id = ?", (block_id,)).fetchone() is None:
            raise HTTPException(404, "block not found")
        conn.execute("DELETE FROM blocks WHERE id = ?", (block_id,))
    return None
