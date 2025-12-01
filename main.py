import sys
import base64
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QDateEdit,
    QMessageBox,
    QGroupBox,
    QAbstractItemView,
)

import db
import imprimir  # <-- NUEVO: módulo externo para la impresión
import os
import tempfile
import shutil
import subprocess


APP_DIR = Path(__file__).resolve().parent


# ==========================
#   ICONO RETRO EN MEMORIA
# ==========================

def create_icon_retro() -> QIcon:
    """Crea un icono retro desde un PNG en base64 (no se guarda en disco)."""
    ICON_BASE64 = b"""
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABgUlEQVRYR+2WwU4CQRCG
vxKkAUkAUkASRAVJAEqQBSDJ2YMBX1IzBgE4tiY2NPz6mfF9V9VpmmZtvuXee+52vvvT
ATzPM8z7D8BlxXQI9CcnVZoAxtuLtgBzBljVGfY1Na4B4tYjdgAjkQq7U7sjppIHHZrL
Pk4A0NlQBV0O8fWVQLAYHzQFOJZpGQEi6f2gG+648FtKQ1wHnauTkPYX8B8AcJh6iD0C
vUTB6gBrN0kPCuBuPwhq+9sG5f4LZDRkADPkE4o6y6Pq4xqDbgJ6oCBO4FmeKcIDai8m
GBQyW9jj4q7l+IaXyhwG3H5KQ8K4Dsr4XJOCou8yb8Yr4x9q69/MDkGfBk4CvwR4FJqX
dFVH/oSEnB4+Mc9YLVgOvdKnY7u+pjHKv6B0G2d9I8nZC3l2qgOLNmo2D4p8zwEWJhtL
IP/dBjLGTJuu8e/AAgggAACCCCAAIIIAAAggggAACCDwX+AQ9dY1AoJpU8wAAAABJRU5E
rkJggg==
    """
    data = base64.b64decode(ICON_BASE64)
    pix = QPixmap()
    pix.loadFromData(data)
    return QIcon(pix)


# ==========================
#   ESTILO GLOBAL (AZUL/NEGRO)
# ==========================

GLOBAL_STYLESHEET = """
/* Fondo general */
QWidget {
    background-color: #050712;
    color: #e5e7eb;
    font-family: "Segoe UI", "Arial";
    font-size: 13px;
}

QMainWindow {
    background-color: #050712;
}

/* Barra de título superior */
QLabel#HeaderTitle {
    background-color: #0a1024;
    border-bottom: 1px solid #1f3b70;
    padding: 10px 18px;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 1px;
    color: #f9fafb;
}

/* Panel lateral izquierdo y derecho */
QWidget#Sidebar, QWidget#ActionsPanel {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #0b1022,
        stop:1 #050712
    );
    border: 1px solid #1e293b;
    border-radius: 12px;
}

QWidget#Sidebar QLabel,
QWidget#ActionsPanel QLabel {
    color: #9ca3af;
}

/* Lista de videojuegos */
QListWidget {
    background-color: #050816;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #1d4ed8;
    selection-color: #f9fafb;
}

/* Cuadro de búsqueda */
QLineEdit {
    background-color: #050816;
    color: #e5e7eb;
    border: 1px solid #1d4ed8;
    border-radius: 6px;
    padding: 6px 8px;
}

/* Fecha */
QDateEdit {
    background-color: #050816;
    color: #e5e7eb;
    border: 1px solid #1d4ed8;
    border-radius: 6px;
    padding: 4px 6px;
}

/* Tarjeta de detalles del videojuego */
QGroupBox#DetailsCard {
    background-color: #050816;
    border: 1px solid #1f2937;
    border-radius: 12px;
    margin-top: 8px;
    padding-top: 14px;
}
QGroupBox#DetailsCard::title {
    color: #60a5fa;
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
}

/* Marco de imagen grande */
#previewBox {
    border: 2px solid #3b82f6;
    border-radius: 16px;
    background-color: #020617;
}

/* Botones generales */
QPushButton {
    background-color: #111827;
    color: #e5e7eb;
    border: 1px solid #2563eb;
    padding: 7px 12px;
    border-radius: 8px;
}
QPushButton:hover {
    background-color: #1f2937;
    border-color: #3b82f6;
}

/* Botón principal (Imprimir ficha) */
QPushButton#PrimaryButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #2563eb,
        stop:1 #38bdf8
    );
    color: #f9fafb;
    border: none;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1d4ed8,
        stop:1 #22d3ee
    );
}

/* Botón peligro (Eliminar) */
QPushButton#DangerButton {
    background-color: #111827;
    color: #fecaca;
    border: 1px solid #ef4444;
}
QPushButton#DangerButton:hover {
    background-color: #7f1d1d;
    border-color: #f87171;
}

/* Mensajes */
QMessageBox {
    background-color: #050712;
    color: #e5e7eb;
}
"""


# ==========================
#   FORMULARIO NUEVO / EDITAR
# ==========================

class GameForm(QDialog):
    """
    Diálogo para crear o editar un videojuego.
    Maneja:
      - title        (nombre)
      - company      (compañía)
      - release_date (fecha)
      - image_data   (bytes de la imagen)
    """

    def __init__(self, parent=None, data: Optional[Dict] = None):
        super().__init__(parent)
        self.setWindowTitle("Ficha de videojuego")
        self.setMinimumWidth(420)

        self.data = data or {}

        # Normalizar image_data por si viene como memoryview desde PostgreSQL
        img = self.data.get("image_data")
        if isinstance(img, memoryview):
            img = img.tobytes()
        self.image_data: Optional[bytes] = img

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Campos
        self.title_edit = QLineEdit(self.data.get("title", ""))
        self.company_edit = QLineEdit(self.data.get("company", ""))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        if self.data.get("release_date"):
            try:
                y, m, d = map(int, str(self.data["release_date"]).split("-"))
                self.date_edit.setDate(QDate(y, m, d))
            except Exception:
                self.date_edit.setDate(QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())

        form.addRow("Nombre del videojuego:", self.title_edit)
        form.addRow("Compañía creadora:", self.company_edit)
        form.addRow("Fecha de lanzamiento:", self.date_edit)

        layout.addLayout(form)

                # Imagen
        self.img_preview = QLabel("Sin imagen")
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setFixedHeight(180)
        self.img_preview.setObjectName("previewBox")

        if self.image_data:
            self._load_from_bytes(self.image_data)

        btn_pick = QPushButton("Seleccionar imagen...")
        btn_pick.clicked.connect(self.pick_image)

        layout.addWidget(self.img_preview)
        layout.addWidget(btn_pick)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen del videojuego",
            str(Path.home()),
            "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if path:
            try:
                with open(path, "rb") as f:
                    self.image_data = f.read()
                self._load_from_bytes(self.image_data)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen:\n{e}")

    def _load_from_bytes(self, data: bytes):
        pix = QPixmap()
        if pix.loadFromData(data):
            size = self.img_preview.size()
            if size.isEmpty():
                size = QSize(180, 180)
            self.img_preview.setPixmap(
                pix.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.img_preview.setText("Imagen no válida")

    def get_data(self) -> Dict:
        """
        Devuelve un diccionario listo para pasar a db.insert_product / update_product.
        release_date se devuelve como datetime.date (via toPython()).
        """
        return {
            "title": self.title_edit.text().strip(),
            "company": self.company_edit.text().strip(),
            "release_date": self.date_edit.date().toPython(),
            "image_data": self.image_data,
        }


# ==========================
#   VENTANA PRINCIPAL
# ==========================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BitGames Retro - Colección de videojuegos")
        self.setWindowIcon(create_icon_retro())
        self.resize(1200, 700)

        # Datos cargados desde la BD
        self.games: List[Dict] = []

        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal: barra de título + contenido
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        header = QLabel("BitGames - Colección de videojuegos")
        header.setObjectName("HeaderTitle")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Fila principal con tres columnas
        root = QHBoxLayout()
        root.setSpacing(10)
        main_layout.addLayout(root, 1)

        # -------- Columna izquierda: búsqueda + lista --------
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        lbl_search = QLabel("Búsqueda:")
        left_col.addWidget(lbl_search)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Nombre o compañía...")
        self.search_edit.textChanged.connect(self.load_data)
        left_col.addWidget(self.search_edit)

        left_col.addWidget(QLabel("Registros de videojuegos:"))
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.currentRowChanged.connect(self.update_detail_view)
        left_col.addWidget(self.list_widget)

        left_container = QWidget()
        left_container.setLayout(left_col)
        left_container.setFixedWidth(260)
        left_container.setObjectName("Sidebar")
        root.addWidget(left_container)

        # -------- Columna central: detalles + imagen debajo --------
        center_col = QVBoxLayout()
        center_col.setSpacing(12)

        details_group = QGroupBox("Detalles del videojuego")
        details_group.setObjectName("DetailsCard")
        detail_form = QFormLayout()

        self.lbl_id = QLabel()
        self.lbl_title = QLabel()
        self.lbl_company = QLabel()
        self.lbl_date = QLabel()

        detail_form.addRow("ID:", self.lbl_id)
        detail_form.addRow("Nombre:", self.lbl_title)
        detail_form.addRow("Compañía:", self.lbl_company)
        detail_form.addRow("Fecha de lanzamiento:", self.lbl_date)

        details_group.setLayout(detail_form)
        center_col.addWidget(details_group)

        # Imagen grande centrada
        image_container = QVBoxLayout()
        image_container.setSpacing(6)

        image_label_title = QLabel("Portada del videojuego")
        image_label_title.setAlignment(Qt.AlignCenter)
        image_container.addWidget(image_label_title)

        self.preview = QLabel("Sin imagen")
        self.preview.setObjectName("previewBox")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedSize(320, 320)
        image_container.addWidget(self.preview, 0, Qt.AlignCenter)

        center_col.addLayout(image_container)

        root.addLayout(center_col, 1)

        # -------- Columna derecha: acciones CRUD + imprimir --------
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        btn_new = QPushButton("Agregar nuevo")
        btn_edit = QPushButton("Editar")
        btn_delete = QPushButton("Eliminar")
        btn_print = QPushButton("Imprimir ficha")

        btn_delete.setObjectName("DangerButton")
        btn_print.setObjectName("PrimaryButton")

        btn_new.clicked.connect(self.on_new)
        btn_edit.clicked.connect(self.on_edit)
        btn_delete.clicked.connect(self.on_delete)
        btn_print.clicked.connect(self.on_print)

        right_col.addWidget(btn_new)
        right_col.addWidget(btn_edit)
        right_col.addSpacing(20)
        right_col.addWidget(btn_delete)
        right_col.addStretch(1)
        right_col.addWidget(btn_print)

        right_container = QWidget()
        right_container.setLayout(right_col)
        right_container.setFixedWidth(190)
        right_container.setObjectName("ActionsPanel")
        root.addWidget(right_container)

        # -------- Inicializar BD y cargar datos --------
        try:
            db.init_db()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error de conexión",
                f"No se pudo conectar al servidor de base de datos:\n{e}",
            )
        self.load_data()

    # -------- Utilidades --------

    def current_game(self) -> Optional[Dict]:
        idx = self.list_widget.currentRow()
        if idx < 0 or idx >= len(self.games):
            return None
        return self.games[idx]

    # -------- Carga de datos --------

    def load_data(self, *_args, select_id: Optional[int] = None):
        search = self.search_edit.text().strip()
        try:
            items = db.list_products(search)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos:\n{e}")
            return

        self.games = items
        self.list_widget.clear()

        selected_index = -1
        for idx, game in enumerate(items):
            display = f"{game.get('id')} - {game.get('title', 'Sin título')}"
            self.list_widget.addItem(display)
            if select_id is not None and game.get("id") == select_id:
                selected_index = idx

        if selected_index != -1:
            self.list_widget.setCurrentRow(selected_index)
        elif self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        else:
            self.update_detail_view(-1)

    # -------- Vista de detalles --------

    def update_detail_view(self, current_row: int):
        game = self.current_game()
        if not game:
            for lbl in (self.lbl_id, self.lbl_title, self.lbl_company, self.lbl_date):
                lbl.setText("")
            self.preview.setText("Sin imagen")
            self.preview.setPixmap(QPixmap())
            return

        self.lbl_id.setText(str(game.get("id", "")))
        self.lbl_title.setText(game.get("title", ""))
        self.lbl_company.setText(game.get("company", ""))
        self.lbl_date.setText(game.get("release_date", ""))

        image_data = game.get("image_data")
        if image_data:
            # Si PostgreSQL devuelve BYTEA como memoryview, lo convertimos a bytes
            if isinstance(image_data, memoryview):
                image_data = image_data.tobytes()

            pix = QPixmap()
            if pix.loadFromData(image_data):
                self.preview.setPixmap(
                    pix.scaled(
                        self.preview.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
            else:
                self.preview.setText("Imagen no válida")
        else:
            self.preview.setText("Sin imagen")


    # -------- Acciones CRUD --------

    def on_new(self):
        dlg = GameForm(self)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()

        if not data["title"] or not data["company"]:
            QMessageBox.warning(
                self, "Campos requeridos", "Nombre y Compañía son obligatorios."
            )
            return

        if not data["image_data"]:
            QMessageBox.warning(
                self,
                "Imagen requerida",
                "Cada registro debe tener su propia imagen.",
            )
            return

        try:
            new_id = db.insert_product(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")
            return

        self.load_data(select_id=new_id)

    def on_edit(self):
        current = self.current_game()
        if not current:
            QMessageBox.information(self, "Editar", "Selecciona un registro primero.")
            return

        # Cargar la versión más reciente desde la BD (por si otro cliente cambió algo)
        game = db.get_product(current["id"])
        if not game:
            QMessageBox.warning(self, "Editar", "El registro ya no existe.")
            self.load_data()
            return

        dlg = GameForm(self, game)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        if not data["title"] or not data["company"]:
            QMessageBox.warning(
                self, "Campos requeridos", "Nombre y Compañía son obligatorios."
            )
            return

        try:
            db.update_product(game["id"], data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar:\n{e}")
            return

        self.load_data(select_id=game["id"])

    def on_delete(self):
        current = self.current_game()
        if not current:
            QMessageBox.information(self, "Eliminar", "Selecciona un registro primero.")
            return

        if (
            QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Eliminar el videojuego '{current.get('title')}'?",
            )
            != QMessageBox.Yes
        ):
            return

        try:
            db.delete_product(current["id"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")
            return

        self.load_data()

    # -------- Impresión (delegada a imprimir.py) --------

    def on_print(self):
        game = self.current_game()
        if not game:
            QMessageBox.information(
                self,
                "Imprimir ficha",
                "Selecciona un videojuego en la lista para imprimir su ficha.",
            )
            return

        # Si se definió PRINT_SERVER_URL en el entorno, intentamos enviar al servidor
        server = os.getenv("PRINT_SERVER_URL")

        # Create a temporary PDF file for preview / download
        fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        # Try render with server-side renderer (reportlab). If that fails,
        # we'll still allow local printing.
        rendered = False
        try:
            imprimir.render_ficha_to_pdf(game, tmp_pdf)
            rendered = True
        except Exception as e:
            # Could not render PDF (e.g., reportlab missing). We'll still let
            # the user print locally via the Qt preview/print flow below.
            rendered = False

        # Build a custom message box with options
        msg = QMessageBox(self)
        msg.setWindowTitle("Imprimir ficha")
        msg.setText(f"Ficha: {game.get('title', 'Sin título')}")
        msg.setInformativeText("Elige una acción: vista previa, descargar PDF o imprimir.")

        btn_preview = msg.addButton("Vista previa", QMessageBox.ActionRole)
        btn_download = msg.addButton("Descargar PDF", QMessageBox.ActionRole)
        btn_print_local = msg.addButton("Imprimir local", QMessageBox.ActionRole)
        btn_cancel = msg.addButton(QMessageBox.Cancel)
        btn_print_server = None
        if server:
            btn_print_server = msg.addButton("Enviar al servidor", QMessageBox.ActionRole)

        msg.exec()

        chosen = msg.clickedButton()

        # Preview: if PDF was rendered, open system PDF viewer. Otherwise, open
        # the local Qt preview dialog (imprimir_ficha) which draws via QPrinter.
        try:
            if chosen == btn_preview:
                if rendered:
                    # open with platform default viewer
                    if sys.platform.startswith("win"):
                        os.startfile(tmp_pdf)  # type: ignore
                    elif sys.platform.startswith("darwin"):
                        subprocess.Popen(["open", tmp_pdf])
                    else:
                        subprocess.Popen(["xdg-open", tmp_pdf])
                else:
                    # fallback to local gui preview/print
                    imprimir.imprimir_ficha(game, parent=self)

            elif chosen == btn_download:
                if not rendered:
                    # attempt render now
                    try:
                        imprimir.render_ficha_to_pdf(game, tmp_pdf)
                        rendered = True
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"No se pudo generar PDF: {e}")
                if rendered:
                    dest, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"{game.get('title','ficha')}.pdf", "PDF Files (*.pdf)")
                    if dest:
                        try:
                            shutil.copy(tmp_pdf, dest)
                            QMessageBox.information(self, "Descarga", f"PDF guardado en: {dest}")
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"No se pudo guardar PDF: {e}")

            elif btn_print_server and chosen == btn_print_server:
                try:
                    ok = imprimir.imprimir_via_servidor(server, game)
                    if ok:
                        QMessageBox.information(self, "Impresión", "Trabajo enviado al servidor de impresión.")
                    else:
                        QMessageBox.critical(self, "Error", "El servidor respondió con error.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo enviar al servidor: {e}")

            elif chosen == btn_print_local:
                # Local printing allows the user to select a printer and print.
                # We keep the existing GUI printing flow which uses a preview dialog
                # and the native Qt print dialog.
                try:
                    imprimir.imprimir_ficha(game, parent=self)
                except Exception as e:
                    QMessageBox.critical(self, "Error de impresión", f"No se pudo imprimir:\n{e}")

        finally:
            try:
                os.remove(tmp_pdf)
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error de impresión", f"No se pudo imprimir:\n{e}")


# ==========================
#   ENTRADA PRINCIPAL
# ==========================

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
