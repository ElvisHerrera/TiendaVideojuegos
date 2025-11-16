# Videogame Store App (PySide6 + SQLite)

Aplicación de escritorio hecha en **Python + PySide6** con **SQLite**.  
Permite hacer CRUD de videojuegos con imagen de portada y cuenta con una vista previa de impresión tipo ficha de producto.

Funciona tanto en **Windows** como en **Linux**.  
En este documento se explica cómo abrir el proyecto en VSCode, cómo ejecutarlo y cómo generar los ejecutables.

---

## 1. Requisitos generales

- **Python 3.10+**
- **Git** (opcional pero recomendado)
- [**Visual Studio Code**](https://code.visualstudio.com/)
- Extensión de VSCode: **Python** (de Microsoft)
- Librerías Python:
  - `PySide6`
  - (las demás vienen en `requirements.txt`)

---

## 2. Clonar el repositorio

Desde una terminal (CMD/PowerShell en Windows o terminal en Linux):

```bash
git clone https://github.com/ElvisHerrera/TiendaVideojuegos.git
cd TiendaVideojuegos
```

El contenido del proyecto queda dentro de esta carpeta.

---

## 3. Abrir y editar el proyecto en VSCode

1. Abrir Visual Studio Code.
2. Ir a **Archivo → Abrir carpeta…**.
3. Seleccionar la carpeta del proyecto clonada: `TiendaVideojuegos`.
4. Aceptar.

VSCode detectará el proyecto y, si existe el entorno virtual `.venv`, normalmente lo sugerirá como intérprete de Python.  
Si no:

- Presiona `Ctrl+Shift+P` → escribe **Python: Select Interpreter** → elige el que apunte a `.venv`.

---

## 4. Configurar entorno y ejecutar en modo desarrollo

### 4.1. Windows

En la terminal de VSCode (dentro del proyecto):

```bash
# Crear entorno virtual (solo la primera vez)
py -m venv .venv

# Activar el entorno
.\.venv\Scriptsctivate

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar la app
python main.py
```

Cada vez que quieras volver a ejecutar el proyecto:

```bash
cd TiendaVideojuegos
.\.venv\Scriptsctivate
python main.py
```

---

### 4.2. Linux (Ubuntu/Debian o similares)

En la terminal (dentro del proyecto):

```bash
# Crear entorno virtual (solo la primera vez)
python3 -m venv .venv

# Activar el entorno
source .venv/bin/activate

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar la app
python3 main.py
```

Para ejecutar otra vez más adelante:

```bash
cd TiendaVideojuegos
source .venv/bin/activate
python3 main.py
```

> La base de datos SQLite se crea y gestiona automáticamente a través del archivo `db.py`.

---

## 5. Generar ejecutable para **Windows** (`.exe`)

1. Abre VSCode en la carpeta del proyecto.
2. Activa el entorno virtual:

   ```bash
   .\.venv\Scripts\activate
   ```

3. Instala **PyInstaller** (si aún no está instalado):

   ```bash
   pip install pyinstaller
   ```

4. Genera el ejecutable:

   ```bash
   pyinstaller --onefile --windowed --name TiendaVideojuegos main.py
   ```

- El archivo `.exe` se generará en la carpeta:

  ```text
  dist/TiendaVideojuegos.exe
  ```

5. Para distribuir la app en otra PC con Windows, copia:

   - `dist/TiendaVideojuegos.exe`
   - La carpeta `media/` (si usas imágenes cargadas desde ahí)
   - Cualquier otro recurso necesario (por ejemplo `assets/` o el archivo de base de datos, si corresponde).

---

## 6. Generar ejecutable para **Linux**

En Linux, con el entorno virtual activado:

```bash
source .venv/bin/activate
pip install pyinstaller
pyinstaller --onefile --windowed --name tienda_juegos main.py
```

- El ejecutable se generará en:

  ```text
  dist/tienda_juegos
  ```

Para ejecutarlo:

```bash
cd dist
./tienda_juegos
```

> Si da problemas de permisos, usar:  
> `chmod +x tienda_juegos` y luego volver a ejecutar.

---

## 7. Estructura del proyecto

```text
TiendaVideojuegos/
├── assets/             # Recursos opcionales (iconos, etc.)
├── media/              # Imágenes copiadas de los videojuegos
├── db.py               # Lógica de conexión y operaciones con SQLite
├── main.py             # Interfaz gráfica (PySide6)
├── README.md           # Este archivo
└── requirements.txt    # Dependencias del proyecto
```

---

## 8. Notas finales

- En modo desarrollo se recomienda **no borrar** la carpeta `media/`, ya que ahí se almacenan las imágenes seleccionadas desde la app.
- Si cambias versiones de Python o librerías, es buena idea eliminar `.venv` y volver a crear el entorno desde cero.
- La vista previa de impresión abre un formulario con la ficha del videojuego; el botón **Imprimir** usa el cuadro de impresión del sistema (Windows o Linux) para enviar ese formulario a la impresora.
