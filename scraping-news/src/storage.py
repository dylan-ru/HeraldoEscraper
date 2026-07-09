import csv
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

from src.config import OUTPUT_DIR, DEFAULT_OUTPUT_FORMAT


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_to_csv(articles: List[Dict], filename: Optional[str] = None) -> str:
    ensure_output_dir()

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"articles_{timestamp}.csv"

    filepath = os.path.join(OUTPUT_DIR, filename)

    if not articles:
        print("[WARN] No hay artículos para guardar.")

    fieldnames = [
        "title",
        "author",
        "date",
        "description",
        "image_url",
        "article_url",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for article in articles:
            row = {k: article.get(k, "") for k in fieldnames}
            writer.writerow(row)

    print(f"[OK] {len(articles)} artículos guardados en {filepath}")
    return filepath


def save_to_sqlite(articles: List[Dict], db_name: Optional[str] = None) -> str:
    ensure_output_dir()

    if not db_name:
        timestamp = datetime.now().strftime("%Y%m%d")
        db_name = f"articles_{timestamp}.db"

    db_path = os.path.join(OUTPUT_DIR, db_name)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            date TEXT,
            description TEXT,
            image_url TEXT,
            article_url TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_article_url ON articles(article_url)
    """)

    inserted_count = 0

    for article in articles:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (title, author, date, description, image_url, article_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                article.get("title"),
                article.get("author"),
                article.get("date"),
                article.get("description"),
                article.get("image_url"),
                article.get("article_url"),
            ))
            if cursor.rowcount > 0:
                inserted_count += 1
        except sqlite3.Error as e:
            print(f"[ERROR] Insertando artículo: {e}")

    conn.commit()
    conn.close()

    print(f"[OK] {inserted_count} artículos nuevos guardados en {db_path}")
    return db_path


def save_articles(articles: List[Dict],
                  output_format: Optional[str] = None,
                  filename: Optional[str] = None) -> str:
    if not output_format:
        output_format = DEFAULT_OUTPUT_FORMAT

    if output_format == "sqlite":
        return save_to_sqlite(articles, filename)
    else:
        return save_to_csv(articles, filename)


def load_from_sqlite(db_path: str) -> List[Dict]:
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
    rows = cursor.fetchall()

    articles = []
    for row in rows:
        articles.append({
            "id": row["id"],
            "title": row["title"],
            "author": row["author"],
            "date": row["date"],
            "description": row["description"],
            "image_url": row["image_url"],
            "article_url": row["article_url"],
            "created_at": row["created_at"],
        })

    conn.close()
    return articles
