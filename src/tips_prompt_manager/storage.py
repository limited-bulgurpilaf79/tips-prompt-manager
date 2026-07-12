"""SQLite storage for categories and prompts."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .auth import now_text

DEFAULT_CATEGORY = "未分类"


class PromptRepository:
    def __init__(self, db_path: Path | str):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def _initialize(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
                """
            )
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category_id INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(category_id) REFERENCES categories(id)
                        ON DELETE SET NULL
                )
                """
            )
            if not self.get_category_by_name(DEFAULT_CATEGORY):
                self.add_category(DEFAULT_CATEGORY)

    def close(self) -> None:
        self.connection.close()

    def list_categories(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT id, name FROM categories ORDER BY name COLLATE NOCASE"
        ).fetchall()

    def get_category_by_name(self, name: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT id, name FROM categories WHERE name = ?", (name,)
        ).fetchone()

    def add_category(self, name: str) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO categories(name, created_at) VALUES(?, ?)",
                (name, now_text()),
            )
        return int(cursor.lastrowid)

    def rename_category(self, category_id: int, name: str) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE categories SET name = ? WHERE id = ?", (name, category_id)
            )

    def delete_category(self, category_id: int) -> None:
        fallback = self.get_category_by_name(DEFAULT_CATEGORY)
        if fallback is None:
            fallback_id = self.add_category(DEFAULT_CATEGORY)
        else:
            fallback_id = int(fallback["id"])
        with self.connection:
            self.connection.execute(
                "UPDATE prompts SET category_id = ? WHERE category_id = ?",
                (fallback_id, category_id),
            )
            self.connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    def list_prompts(self, category_id: int | None = None, query: str = "") -> list[sqlite3.Row]:
        params: list[object] = []
        conditions: list[str] = []
        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        if query:
            conditions.append("(p.title LIKE ? OR p.content LIKE ?)")
            keyword = f"%{query}%"
            params.extend([keyword, keyword])
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return self.connection.execute(
            f"""
            SELECT p.id, p.title, p.content, p.category_id, p.updated_at,
                   COALESCE(c.name, ?) AS category_name
            FROM prompts p
            LEFT JOIN categories c ON c.id = p.category_id
            {where}
            ORDER BY p.updated_at DESC, p.id DESC
            """,
            [DEFAULT_CATEGORY, *params],
        ).fetchall()

    def get_prompt(self, prompt_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT p.id, p.title, p.content, p.category_id, p.created_at, p.updated_at,
                   COALESCE(c.name, ?) AS category_name
            FROM prompts p
            LEFT JOIN categories c ON c.id = p.category_id
            WHERE p.id = ?
            """,
            (DEFAULT_CATEGORY, prompt_id),
        ).fetchone()

    def save_prompt(
        self, prompt_id: int | None, title: str, content: str, category_id: int
    ) -> int:
        timestamp = now_text()
        with self.connection:
            if prompt_id:
                self.connection.execute(
                    """
                    UPDATE prompts
                    SET title = ?, content = ?, category_id = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (title, content, category_id, timestamp, prompt_id),
                )
                return prompt_id
            cursor = self.connection.execute(
                """
                INSERT INTO prompts(title, content, category_id, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (title, content, category_id, timestamp, timestamp),
            )
        return int(cursor.lastrowid)

    def delete_prompt(self, prompt_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
