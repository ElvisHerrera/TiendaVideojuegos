# Videogame Store App (PySide6 + PostgreSQL en red)

Aplicación de escritorio hecha en **Python + PySide6** con **PostgreSQL** como base de datos centralizada.

- Permite hacer **CRUD** de videojuegos con **imagen de portada** almacenada en PostgreSQL (columna `BYTEA`).
- Incluye función de **impresión de ficha** del videojuego actual (usando el cuadro de impresión nativo del sistema).
- Los clientes pueden correr en **Windows 11** y en **Linux (Ubuntu 25.10)** conectándose por red a una **laptop servidor** que tiene PostgreSQL.

---

## 1. Requisitos

### En la máquina cliente (donde corre la app)

- Python 3.10 o superior  
- Git (opcional)  
- Visual Studio Code  
- Extensión de VSCode: Python (de Microsoft)  
- Librerías Python (se instalan desde `requirements.txt`):
  - PySide6
  - psycopg2-binary
  - otras que incluya el proyecto

### En la máquina servidor (base de datos)

- PostgreSQL (por ejemplo PostgreSQL 18)  
- pgAdmin (opcional, para administrar PostgreSQL)  
- Base de datos, usuario y permisos configurados. Ejemplo:
  - BD: `tienda_videojuegos`
  - Usuario: `tienda_user`
  - Contraseña: `TuPasswordSegura123`
- El servidor debe permitir conexiones desde la red local (ajustes en `postgresql.conf` y `pg_hba.conf`).

La tabla `videogame` se crea automáticamente al iniciar la app, a través de `db.py`:

    CREATE TABLE IF NOT EXISTS videogame (
        id           SERIAL PRIMARY KEY,
        title        VARCHAR(200) NOT NULL,
        company      VARCHAR(200) NOT NULL,
        release_date DATE NOT NULL,
        image_data   BYTEA NOT NULL
    );

---

## 2. Clonar el repositorio

Desde una terminal (CMD o PowerShell en Windows, o terminal en Linux):

    git clone https://github.com/ElvisHerrera/TiendaVideojuegos.git
    cd TiendaVideojuegos

---

## 3. Configurar la conexión a PostgreSQL (db.py)

En el archivo `db.py` se configura el servidor de base de datos. Ejemplo:

    DB_HOST = "192.168.56.1"      # IP de la laptop servidor
    DB_PORT = 5432
    DB_NAME = "tienda_videojuegos"
    DB_USER = "tienda_user"
    DB_PASSWORD = "TuPasswordSegura123"

Antes de ejecutar la app:

1. Verificar que PostgreSQL está corriendo en la laptop servidor.  
2. Ajustar `DB_HOST`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` a tu entorno.  
3. Revisar que `pg_hba.conf` permite la IP de los clientes.

Las portadas se guardan directamente en la columna `image_data` (BYTEA), así que cualquier cliente que se conecte a la misma BD verá las mismas imágenes.

---

## 4. Abrir el proyecto en VSCode

1. Abrir Visual Studio Code.  
2. Ir a Archivo → Abrir carpeta.  
3. Seleccionar la carpeta del proyecto `TiendaVideojuegos`.  
4. Presionar `Ctrl+Shift+P` → escribir `Python: Select Interpreter` → elegir el intérprete que apunte a `.venv` (cuando exista).

---

## 5. Configurar entorno y ejecutar en modo desarrollo

### 5.1. Windows

En la terminal de VSCode (dentro del proyecto):

    py -m venv .venv               # Crear entorno virtual (solo la primera vez)
    .\.venv\Scripts\activate       # Activar el entorno
    pip install --upgrade pip      # Actualizar pip
    pip install -r requirements.txt
    python main.py                 # Ejecutar la app

Para volver a ejecutar la app más adelante:

    cd TiendaVideojuegos
    .\.venv\Scripts\activate
    python main.py

### 5.2. Linux (Ubuntu, Debian o similares)

En la terminal (dentro del proyecto):

    python3 -m venv .venv          # Crear entorno virtual (solo la primera vez)
    source .venv/bin/activate      # Activar el entorno
    pip install --upgrade pip      # Actualizar pip
    pip install -r requirements.txt
    python3 main.py                # Ejecutar la app

Para ejecutarla de nuevo:

    cd TiendaVideojuegos
    source .venv/bin/activate
    python3 main.py

La app siempre se conecta al servidor PostgreSQL usando la configuración de `db.py`. No se usan archivos de base de datos locales.

---

## 6. Generar ejecutable para Windows (exe)

Con el entorno virtual activo en Windows:

    .\.venv\Scripts\activate
    pip install pyinstaller
    pyinstaller --onefile --windowed --name TiendaVideojuegos main.py

El ejecutable quedará en:

    dist/TiendaVideojuegos.exe

Para usarlo en otra PC con Windows:

- Copiar `dist/TiendaVideojuegos.exe`.  
- Asegurar que esa PC puede conectarse a la IP de la laptop servidor (misma red).  
- No hace falta copiar ninguna base de datos local, porque los datos están en PostgreSQL.

---

## 7. Generar ejecutable para Linux

Con el entorno virtual activo en Linux:

    source .venv/bin/activate
    pip install pyinstaller
    pyinstaller --onefile --windowed --name tienda_juegos main.py

El ejecutable quedará en:

    dist/tienda_juegos

Para ejecutarlo:

    cd dist
    chmod +x tienda_juegos   # si es necesario
    ./tienda_juegos

El ejecutable se conecta al mismo servidor PostgreSQL configurado en `db.py`.

---

## 8. Estructura del proyecto

    TiendaVideojuegos/
    ├── assets/             # Recursos opcionales (iconos, etc.)
    ├── db.py               # Conexión y CRUD con PostgreSQL (incluye image_data BYTEA)
    ├── imprimir.py         # Lógica de impresión de la ficha del videojuego
    ├── main.py             # Interfaz gráfica (PySide6)
    ├── README.md           # Este archivo
    └── requirements.txt    # Dependencias del proyecto

Las imágenes de los videojuegos no se guardan en carpetas locales, sino en PostgreSQL (columna `image_data`). Esto permite que varias máquinas (Windows y Linux) vean la misma información y portadas.

---

## 9. Flujo de uso

1. En la laptop servidor:
   - Levantar el servicio PostgreSQL.  
   - Asegurar que existen:
     - BD `tienda_videojuegos`.
     - Usuario `tienda_user` con permisos sobre la BD, la tabla `videogame` y la secuencia `videogame_id_seq`.

2. En las laptops cliente (Windows o Ubuntu):
   - Activar `.venv` y ejecutar `python main.py` o usar el ejecutable generado.  
   - Agregar videojuegos con:
     - Nombre.
     - Compañía.
     - Fecha de lanzamiento.
     - Imagen de portada (se guarda como BYTEA).

3. Para imprimir la ficha:
   - Seleccionar un videojuego en la lista.  
   - Pulsar el botón "Imprimir ficha".  
   - El módulo `imprimir.py` abre el cuadro de impresión nativo (Windows o Linux) y envía título, datos y portada a la impresora seleccionada.

---

## 10. Notas finales

- Mensajes en consola como `libpng error: Read Error` suelen ser avisos internos de los plugins de imagen de Qt cuando prueban distintos formatos (por ejemplo, intentan leer un JPG como PNG). Mientras la imagen se vea bien en la app, no es un fallo crítico.
- Si cambias la IP del servidor o la configuración de PostgreSQL, recuerda actualizar `DB_HOST`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` en `db.py`.
- Si aparecen errores de permisos en PostgreSQL (permission denied, problemas con secuencias, etc.), revisa:
  - Permisos del rol `tienda_user` sobre la BD, el esquema `public`, la tabla `videogame` y la secuencia `videogame_id_seq`.
  - Configuración de `pg_hba.conf` y el reinicio del servicio PostgreSQL.
