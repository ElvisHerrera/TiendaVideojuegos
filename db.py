import os
import sqlite3
from pathlib import Path

# ============================================================
#  UBICACIÓN PERMANENTE DE LA BASE DE DATOS (LINUX + WINDOWS)
# ============================================================

def get_app_dir():
    if os.name == "nt":  # Windows
        base = os.path.join(os.environ.get("APPDATA"), "tienda_juegos")
    else:  # Linux/Mac
        base = os.path.expanduser("~/.local/share/tienda_juegos")

    if not os.path.exists(base):
        os.makedirs(base)

    return base


def get_db_path():
    return os.path.join(get_app_dir(), "database.db")


# ============================================================
#  CONEXIÓN DE BASE DE DATOS
# ============================================================

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
#  INICIALIZAR BASE DE DATOS
# ============================================================

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            platform TEXT NOT NULL,
            genre TEXT,
            price REAL NOT NULL CHECK(price >= 0),
            stock INTEGER NOT NULL DEFAULT 0,
            image_path TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Trigger para actualizar updated_at
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS product_updated_at
        AFTER UPDATE ON product
        BEGIN
            UPDATE product SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )

    conn.commit()
    conn.close()


# ============================================================
#  CRUD
# ============================================================

def list_products(search=""):
    conn = get_connection()
    cur = conn.cursor()

    if search:
        like = f"%{search}%"
        cur.execute(
            """
            SELECT * FROM product
            WHERE title LIKE ? OR platform LIKE ? OR genre LIKE ?
            ORDER BY id DESC
            """,
            (like, like, like)
        )
    else:
        cur.execute("SELECT * FROM product ORDER BY id DESC")

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_product(pid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM product WHERE id = ?", (pid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def insert_product(data: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO product (title, platform, genre, price, stock, image_path, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("title", "").strip(),
            data.get("platform", "").strip(),
            data.get("genre", "").strip(),
            float(data.get("price", 0)),
            int(data.get("stock", 0)),
            data.get("image_path"),
            data.get("description", "").strip(),
        ),
    )

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_product(pid: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE product SET
            title=?, platform=?, genre=?, price=?, stock=?, image_path=?, description=?
        WHERE id=?
        """,
        (
            data.get("title", "").strip(),
            data.get("platform", "").strip(),
            data.get("genre", "").strip(),
            float(data.get("price", 0)),
            int(data.get("stock", 0)),
            data.get("image_path"),
            data.get("description", "").strip(),
            pid,
        )
    )

    conn.commit()
    conn.close()


def delete_product(pid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product WHERE id = ?", (pid,))
    conn.commit()
    conn.close()


# ============================================================
#  CARPETA PARA GUARDAR IMÁGENES
# ============================================================

def get_media_path():
    media_dir = os.path.join(get_app_dir(), "media")

    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    return media_dir
