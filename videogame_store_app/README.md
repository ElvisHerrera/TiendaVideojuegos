# Videogame Store App (PySide6 + SQLite)

Aplicación de escritorio para Linux hecha en **Python + PySide6** con **SQLite**. 
Permite CRUD de videojuegos con imagen, y trae una **interfaz de impresión simulada** con selección de impresora y **vista previa (Print Preview)**.

## Requisitos
- Python 3.10+
- Linux (probado en Ubuntu/Debian). También corre en Windows.
- Paquetes: `PySide6`

## Instalación (Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Empaquetado (Linux)
```bash
pip install pyinstaller
pyinstaller --onefile --name tienda_juegos main.py
# Binario: dist/tienda_juegos
```

## Estructura
```
videogame_store_app/
├── assets/
├── media/
├── db.py
├── main.py
├── README.md
└── requirements.txt
```
