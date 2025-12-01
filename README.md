---

## 13. Preparar la BD rápidamente y probar la impresión

Si ya tienes PostgreSQL en la máquina servidor, estos son los pasos mínimos para dejar todo listo y probar impresión desde clientes Windows/Ubuntu.

1) Crear rol + base de datos (ejecutar como superusuario `postgres` en psql o desde pgAdmin):

```sql
-- Crear rol
CREATE ROLE tienda_user WITH LOGIN PASSWORD 'TuPasswordSegura123' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;

-- Crear BD (o ajustar owner si ya existe)
CREATE DATABASE tienda_videojuegos WITH OWNER = tienda_user ENCODING = 'UTF8' TEMPLATE = template0;

-- Permisos base
GRANT ALL PRIVILEGES ON DATABASE tienda_videojuegos TO tienda_user;
```

2) Permitir conexiones desde la red (editar `pg_hba.conf` en el servidor y añadir una línea similar):

```
host    tienda_videojuegos    tienda_user    192.168.56.0/24    md5
```

Reinicia PostgreSQL después de editar `pg_hba.conf`.

3) Asegúrate de que el servidor escucha conexiones en la IP/puerto correctos (postgresql.conf -> listen_addresses)

4) Preparar la BD y agregar un registro de prueba desde cualquier máquina que tenga acceso (cliente o servidor):

```bash
# exporta la IP de tu servidor PostgreSQL (reemplaza 192.168.X.Y por la IP real)
export DB_HOST=192.168.X.Y
export DB_PORT=5432
export DB_NAME=tienda_videojuegos
export DB_USER=tienda_user
export DB_PASSWORD=TuPasswordSegura123

# crear tabla (si no existe) e insertar un registro de ejemplo
python3 tests/bootstrap_db_sample.py
```

Si el script informa que insertó un `id`, ya tienes un registro listo para probar la vista previa/impresión desde la app cliente.

5) Arrancar el servicio de impresión en la máquina que tenga la impresora:

```bash
export DB_HOST=192.168.X.Y   # IP del servidor BD si print_server necesita leer la BD
python3 print_server.py
```

6) En el cliente (Windows o Ubuntu) configura la IP del servidor DB y la URL del servidor de impresión y ejecuta la app:

```bash
export DB_HOST=192.168.X.Y
export PRINT_SERVER_URL="http://SERVER_IP:5000"
python3 main.py
```

7) Probar preview por HTTP (útil para debug):

```bash
curl -X GET http://SERVER_IP:5000/preview/id/<id> --output preview.pdf
# Abre preview.pdf en tu sistema para ver el resultado
```

Si algún paso falla, pega el error aquí y lo reviso — puedo ayudarte a ajustar `pg_hba.conf`, permisos o a solucionar problemas de conexión.

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

---

## 11. Pruebas (tests)

Hay un pequeño conjunto de pruebas unitarias para funciones puras del módulo `db.py` que no requieren una base de datos real.

Para ejecutarlas localmente:

1. Crear y activar el entorno virtual (si no existe):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2. Instalar dependencias (incluye pytest):

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3. Ejecutar las pruebas con pytest:

    ```bash
    pytest -q
    ```

Si quieres añadir pruebas de integración que usen PostgreSQL, lo ideal es crear una base de datos de pruebas y exportar las variables de conexión antes de ejecutar esas pruebas, por ejemplo:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tienda_test
export DB_USER=tienda_user
export DB_PASSWORD=MiPassDePrueba
pytest -q
```

De esta forma `db.py` usará variables de entorno si están presentes y no sobrescribirá los valores por defecto.

---

## 12. Impresión centralizada (servidor de impresión)

Si quieres que una PC actúe como *servidor de impresión* (con la impresora física conectada) y acepte solicitudes de impresión desde clientes en Windows o Linux, puedes usar el servicio HTTP incluido en este repo.

1) Preparar el servidor (PC con la impresora conectada)

 - Asegúrate de que la impresora está correctamente instalada y funcionando en esa máquina. En Linux normalmente se usa CUPS (lp/lpr) y en Windows la impresora debe estar registrada en el sistema.
 - Asegúrate de que la impresora está correctamente instalada y funcionando en esa máquina. En Linux normalmente se usa CUPS (lp/lpr) y en Windows la impresora debe estar registrada en el sistema.

### Scripts de ayuda

Para simplificar la puesta en marcha incluimos scripts en `scripts/`:

- `scripts/setup-server.sh` — crea `.venv`, instala dependencias y arranca `print_server.py` en background (guarda logs en `logs/print_server.log`).
- `scripts/setup-client-linux.sh` — prepara el entorno cliente en Linux.
- `scripts/setup-client-windows.ps1` — prepara el entorno cliente en Windows (PowerShell).
- `scripts/print_server.service.example` — ejemplo de service systemd para correr `print_server.py` como servicio.

Ejecuta los scripts desde la raíz del repo (por ejemplo `bash scripts/setup-server.sh`).
 - Crear y activar un entorno virtual y instalar dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2) Ejecutar el servicio de impresión (por ejemplo en la máquina servidor):

```bash
# Ejecuta el servicio Flask que escuchará peticiones HTTP (por defecto en 0.0.0.0:5000)
python3 print_server.py
```

3) Desde un cliente (Windows o Ubuntu)

 - Puedes usar el endpoint `/print/id/<id>` para que el servidor recupere el registro por `id` desde la base de datos y lo envíe a la impresora.
 - O usar `/print/raw` enviando JSON con `title`, `company`, `release_date` y `image_data` (base64) para imprimir datos arbitrarios.

Ejemplo usando curl (envía un job con JSON):

```bash
curl -X POST http://PRINT-SERVER-IP:5000/print/raw \
    -H "Content-Type: application/json" \
    -d '{"title":"Mi Juego","company":"ACME","release_date":"2020-01-01","image_data":null}'
```

O para imprimir un registro que ya está en la BD por id:

```bash
curl -X POST http://PRINT-SERVER-IP:5000/print/id/17
```

### Vista previa / descarga desde la app cliente

La aplicación ahora permite generar una vista previa (PDF) antes de imprimir. Cuando pulses "Imprimir ficha" se dará la opción de:

- Ver vista previa (se abrirá un visor PDF desde la máquina cliente).
- Descargar la ficha en PDF (guardar archivo localmente).
- Imprimir localmente (se abre el diálogo nativo de impresión donde eliges la impresora).
- Enviar al servidor de impresión (si `PRINT_SERVER_URL` está configurado) para imprimir desde la PC que tenga la impresora conectada.

### Conectar la aplicación a tu servidor PostgreSQL (usar tu IP)

Si tu servidor PostgreSQL está en otra máquina en tu red, solo tienes que decirle a la app la IP del servidor. Hay dos opciones:

1) Exportando variables de entorno en la máquina cliente antes de arrancar la app:

```bash
export DB_HOST=192.168.0.42   # cambia por la IP de tu servidor
export DB_PORT=5432
export DB_NAME=tienda_videojuegos
export DB_USER=tienda_user
export DB_PASSWORD=TuPassword
python3 main.py
```

2) Editando `db.py` (no recomendado para producción): cambia `DB_HOST` con la IP de tu servidor.

Si tienes instrucciones adicionales en `/home/harold/Downloads/instrucciones_postgre.txt`, pégamelas aquí y te explico los pasos exactos para tu entorno.

4) Integrar desde la app cliente (opcional)

 - Si quieres que las instancias cliente de la app (Windows/Ubuntu) envíen trabajos al servidor, la función `imprimir.imprimir_via_servidor(server_url, game)` está incluida en `imprimir.py`.

 - En `main.py` la llamada a impresión se mantendrá local por defecto (abre diálogo), pero si estableces la variable de entorno `PRINT_SERVER_URL` (p. ej. `http://mi-servidor:5000`) la app intentará enviar el trabajo al servidor en vez de abrir el diálogo local.

5) Seguridad y red

 - Asegúrate de permitir tráfico entre máquinas sobre el puerto del servidor (por defecto 5000). Para entornos de producción protege el servicio (autenticación, HTTPS, firewall).

---
