# db.py - Acceso a PostgreSQL para colección de videojuegos
import datetime
from typing import List, Dict, Optional

import psycopg2
from psycopg2 import Binary
from psycopg2.extras import RealDictCursor

# ======================
# CONFIGURACIÓN SERVIDOR
# ======================

DB_HOST = "192.168.56.1"      # <-- TU IP DEL SERVIDOR
DB_PORT = 5432
DB_NAME = "tienda_videojuegos"
DB_USER = "tienda_user"
DB_PASSWORD = "P123"   # <-- TU PASSWORD


def get_connection():
    """
    Crea una conexión nueva a PostgreSQL usando RealDictCursor
    para devolver diccionarios en lugar de tuplas.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )
    return conn


def _normalize_date(value) -> str:
    """
    Convierte la fecha que viene de PostgreSQL a 'YYYY-MM-DD' (string),
    para mostrarla fácil en la interfaz.
    """
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    return str(value) if value is not None else ""


def _row_to_dict(row) -> Optional[Dict]:
    """
    Convierte una fila de RealDictCursor a dict normal,
    normalizando fecha e imagen (memoryview -> bytes).
    """
    if not row:
        return None

    d = dict(row)

    # Fecha
    d["release_date"] = _normalize_date(d.get("release_date"))

    # Imagen: PostgreSQL suele devolver BYTEA como memoryview
    img = d.get("image_data")
    if isinstance(img, memoryview):
        d["image_data"] = img.tobytes()

    return d


def init_db():
    """
    Crea la tabla videogame si no existe.
    Se llama una sola vez al iniciar la app.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS videogame (
            id           SERIAL PRIMARY KEY,
            title        VARCHAR(200) NOT NULL,
            company      VARCHAR(200) NOT NULL,
            release_date DATE NOT NULL,
            image_data   BYTEA NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


# ======================
# FUNCIONES CRUD
# ======================

def list_products(search: str = "") -> List[Dict]:
    """
    Lista videojuegos. Si 'search' viene con texto, filtra por título o compañía.
    Devuelve una lista de diccionarios, cada uno con todos los campos,
    incluida la imagen en image_data (bytes).
    """
    conn = get_connection()
    cur = conn.cursor()

    if search:
        like = f"%{search}%"
        cur.execute(
            """
            SELECT id, title, company, release_date, image_data
            FROM videogame
            WHERE title ILIKE %s OR company ILIKE %s
            ORDER BY id DESC
            """,
            (like, like),
        )
    else:
        cur.execute(
            """
            SELECT id, title, company, release_date, image_data
            FROM videogame
            ORDER BY id DESC
            """
        )

    rows = cur.fetchall()
    conn.close()

    result: List[Dict] = []
    for r in rows:
        d = _row_to_dict(r)
        if d is not None:
            result.append(d)
    return result


def get_product(pid: int) -> Optional[Dict]:
    """
    Obtiene un solo videojuego por id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, title, company, release_date, image_data
        FROM videogame
        WHERE id = %s
        """,
        (pid,),
    )
    row = cur.fetchone()
    conn.close()

    return _row_to_dict(row)


def insert_product(data: Dict) -> int:
    """
    Inserta un videojuego. 'data' debe traer:
    - title (str)
    - company (str)
    - release_date (datetime.date)
    - image_data (bytes)
    Devuelve el id generado.
    """
    conn = get_connection()
    cur = conn.cursor()

    image_bytes = data.get("image_data")
    if isinstance(image_bytes, memoryview):
        image_bytes = image_bytes.tobytes()

    cur.execute(
        """
        INSERT INTO videogame (title, company, release_date, image_data)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """,
        (
            data["title"],
            data["company"],
            data["release_date"],
            Binary(image_bytes),
        ),
    )
    new_id_row = cur.fetchone()
    conn.commit()
    conn.close()

    return int(new_id_row["id"])


def update_product(pid: int, data: Dict) -> None:
    """
    Actualiza un videojuego por id.
    Si 'image_data' viene None, conserva la imagen anterior.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Si no hay nueva imagen, tomamos la actual
    image_data = data.get("image_data")
    if image_data is None:
        cur.execute("SELECT image_data FROM videogame WHERE id = %s", (pid,))
        row = cur.fetchone()
        if row:
            img = row["image_data"]
            if isinstance(img, memoryview):
                img = img.tobytes()
            image_data = img
    else:
        if isinstance(image_data, memoryview):
            image_data = image_data.tobytes()

    cur.execute(
        """
        UPDATE videogame
        SET title = %s,
            company = %s,
            release_date = %s,
            image_data = %s
        WHERE id = %s;
        """,
        (
            data["title"],
            data["company"],
            data["release_date"],
            Binary(image_data),
            pid,
        ),
    )
    conn.commit()
    conn.close()


def delete_product(pid: int) -> None:
    """
    Elimina un videojuego por id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM videogame WHERE id = %s", (pid,))
    conn.commit()
    conn.close()
