import sys
import shutil
import base64
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QPixmap, QPainter, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QMessageBox,
    QToolBar,
    QSplitter,
    QAbstractItemView,
    QListWidget, # Se usa para la lista lateral de registros (diseño de base de datos)
    QGroupBox,   # Se usa para agrupar campos (diseño de base de datos)
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

import db
from pathlib import Path
MEDIA_DIR = Path(db.get_media_path())



# =============================
#  🔵 CREA ICONO RETRO (D)
# =============================
def create_icon_retro():
    """Crea un icono retro neon azul desde base64 en media/icon.png"""
    icon_path = MEDIA_DIR / "icon.png"

    if icon_path.exists():
        return icon_path

    # Icono pixel-art azul neon (gamepad simplificado 32x32)
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

    icon_path.write_bytes(base64.b64decode(ICON_BASE64))

    return icon_path


PLATFORMS = ["PC", "PlayStation", "Xbox", "Nintendo", "Steam Deck", "Otro"]


def human_price(p: float) -> str:
    return f"${p:,.2f}"


# ============================
#   🎨 ESTILO GLOBAL RETRO - MATRIX (verde)
# ============================
GLOBAL_STYLESHEET = """
/* General application background */
QWidget {
    background-color: #000000;
    color: #00ff66;
    font-family: "Segoe UI", "Arial";
    font-size: 13px;
}

/* Main window windowframe look */
QMainWindow {
    background-color: #000000;
}

/* Toolbar (se mantiene aunque no se use) */
QToolBar {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #001100, stop:1 #002200);
    border-bottom: 1px solid #003300;
}

/* Buttons */
QPushButton {
    background-color: #002200;
    color: #00ff66;
    border: 1px solid #007700;
    padding: 6px 10px;
    border-radius: 6px;
}
QPushButton:hover {
    background-color: #003300;
    border: 1px solid #00bb44;
}

/* LineEdits and TextEdits */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #001100;
    color: #a8ffb0;
    border: 1px solid #004400;
    padding: 6px;
    border-radius: 4px;
}

/* List Widget (para la lista lateral de registros) */
QListWidget {
    background-color: #000000;
    border: 1px solid #004400;
    selection-background-color: #002200;
    selection-color: #b6ffcc;
}

/* GroupBox (para Detalles y Descripción) */
QGroupBox {
    border: 1px solid #004400;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold; /* Para destacar el título */
}
QGroupBox::title {
    color: #00ff66;
    subcontrol-origin: margin;
    subcontrol-position: top center; 
    padding: 0 5px;
}

/* Preview box (marco para la imagen central) */
#previewBox {
    border: 2px solid #00ff66;
    border-radius: 8px;
    background-color: #001100;
}

/* El resto del estilo se mantiene igual... */

/* ProductPrintPreview specifics */
ProductPrintPreview, QDialog {
    background-color: #000000;
    border: 2px solid #00ff66;
}
#ImageFrame {
    border: 3px solid #00ff66;
    border-radius: 10px;
    background-color: #001100;
}
#TitleLabel {
    color: #00ff66;
    font-size: 20px;
    font-weight: bold;
    text-shadow: 0 0 6px #00ff66;
}

/* Small accent glow lines */
QLabel {
    color: #b6ffcc;
}

/* Message boxes */
QMessageBox {
    background-color: #000000;
    color: #00ff66;
    border: 1px solid #004400;
}
"""


class ProductForm(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        # Título para la ventana de edición de registro
        self.setWindowTitle("Ficha de Producto")
        self.setMinimumWidth(420)
        self.data = data or {}
        self.image_path = self.data.get("image_path")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # --- Campos del formulario (mapean a la tabla de la DB) ---
        self.title = QLineEdit(self.data.get("title", ""))
        self.platform = QComboBox()
        self.platform.addItems(PLATFORMS)
        if self.data.get("platform") in PLATFORMS:
            self.platform.setCurrentText(self.data["platform"])

        self.genre = QLineEdit(self.data.get("genre", ""))
        self.price = QDoubleSpinBox()
        self.price.setRange(0, 9_999_999)
        self.price.setDecimals(2)
        self.price.setValue(float(self.data.get("price", 0)))
        self.stock = QSpinBox()
        self.stock.setRange(0, 999_999)
        self.stock.setValue(int(self.data.get("stock", 0)))
        self.description = QTextEdit(self.data.get("description", ""))

        # Image picker
        self.img_preview = QLabel("Sin imagen")
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setFixedHeight(160)
        self.img_preview.setStyleSheet("border:1px dashed #004400; border-radius:10px;")
        
        if self.image_path and Path(self.image_path).exists():
            self.img_preview.setMinimumSize(QSize(160, 160))
            self._load_preview(self.image_path)
        
        btn_pick = QPushButton("Seleccionar imagen...")
        btn_pick.clicked.connect(self.pick_image)

        form.addRow("Título:", self.title)
        form.addRow("Plataforma:", self.platform)
        form.addRow("Género:", self.genre)
        form.addRow("Precio:", self.price)
        form.addRow("Stock:", self.stock)
        form.addRow("Descripción:", self.description)

        layout.addLayout(form)
        layout.addWidget(self.img_preview)
        layout.addWidget(btn_pick)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def showEvent(self, event):
        if self.image_path and Path(self.image_path).exists():
            self._load_preview(self.image_path)
        super().showEvent(event)


    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            str(Path.home()),
            "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if path:
            self.image_path = path
            self._load_preview(path)

    def _load_preview(self, path: str):
        pix = QPixmap(path)
        if not pix.isNull():
            size = self.img_preview.size()
            if size.isEmpty():
                size = QSize(160, 160)
            
            self.img_preview.setPixmap(
                pix.scaled(
                    size, 
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            self.img_preview.setText("Imagen no válida")

    def get_data(self) -> dict:
        return {
            "title": self.title.text().strip(),
            "platform": self.platform.currentText(),
            "genre": self.genre.text().strip(),
            "price": float(self.price.value()),
            "stock": int(self.stock.value()),
            "description": self.description.toPlainText().strip(),
            "image_path": self.image_path,
        }

class ProductPrintPreview(QDialog):
    def __init__(self, product: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista previa de impresión - Ficha de producto")
        self.resize(800, 600)

        # ... (Contenido de ProductPrintPreview se mantiene igual)
        if hasattr(product, "keys") and not isinstance(product, dict):
            try:
                self.product = {k: product[k] for k in product.keys()}
            except Exception:
                self.product = dict(product)
        else:
            self.product = dict(product or {})

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # TOP BAR
        top_bar = QHBoxLayout()
        btn_back = QPushButton("← Volver")
        btn_print = QPushButton("Imprimir")
        top_bar.addWidget(btn_back)
        top_bar.addStretch(1)
        top_bar.addWidget(btn_print)
        main_layout.addLayout(top_bar)

        body = QHBoxLayout()
        main_layout.addLayout(body, 1)

        left = QVBoxLayout()
        right = QVBoxLayout()
        body.addLayout(left, 2)
        body.addLayout(right, 1)

        # Título
        self.lbl_title = QLabel()
        self.lbl_title.setObjectName("TitleLabel")
        left.addWidget(self.lbl_title)

        form = QFormLayout()
        self.lbl_platform = QLabel()
        self.lbl_genre = QLabel()
        self.lbl_price = QLabel()
        self.lbl_stock = QLabel()

        form.addRow("Plataforma:", self.lbl_platform)
        form.addRow("Género:", self.lbl_genre)
        form.addRow("Precio:", self.lbl_price)
        form.addRow("Stock:", self.lbl_stock)
        left.addLayout(form)

        lbl_desc_title = QLabel("Descripción:")
        self.txt_desc = QTextEdit()
        self.txt_desc.setReadOnly(True)
        self.txt_desc.setFixedHeight(180)
        left.addWidget(lbl_desc_title)
        left.addWidget(self.txt_desc, 1)

        self.img_label = QLabel("Sin imagen")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setObjectName("ImageFrame")
        right.addWidget(self.img_label, 1)

        self._fill_from_product()

        btn_back.clicked.connect(self.reject)
        btn_print.clicked.connect(self._print)

    def _fill_from_product(self):
        p = self.product

        self.lbl_title.setText(p.get("title", ""))
        self.lbl_platform.setText(p.get("platform", ""))
        self.lbl_genre.setText(p.get("genre", ""))
        self.lbl_price.setText(human_price(float(p.get("price") or 0)))
        self.lbl_stock.setText(f"{int(p.get('stock') or 0)} unidades")
        self.txt_desc.setPlainText(p.get("description", ""))

        img_path = p.get("image_path", "")
        if img_path and Path(img_path).exists():
            pix = QPixmap(img_path)
            if not pix.isNull():
                self.img_label.setPixmap(
                    pix.scaled(260, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            else:
                self.img_label.setText("Imagen no válida")
        else:
            self.img_label.setText("Sin imagen")

    def _print(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec() != QDialog.Accepted:
            return

        painter = QPainter(printer)
        try:
            pix = self.grab()
            page_rect = printer.pageRect()
            scaled = pix.scaled(
                page_rect.size().toSize(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            x = page_rect.left() + (page_rect.width() - scaled.width()) / 2
            y = page_rect.top() + (page_rect.height() - scaled.height()) / 2
            painter.drawPixmap(int(x), int(y), scaled)
        finally:
            painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # ⭐ TÍTULO CON DISEÑO DE BASE DE DATOS
        self.setWindowTitle("BitGames Retro")

        # ⭐ ICONO RETRO
        icon_path = create_icon_retro()
        self.setWindowIcon(QIcon(str(icon_path)))

        self.resize(1200, 700)

        # Quitamos la barra de herramientas clásica y la reemplazamos por el panel lateral de acciones
        # self.addToolBar(toolbar) 

        central = QWidget()
        self.setCentralWidget(central)
        main_hlayout = QHBoxLayout(central)
        main_hlayout.setContentsMargins(5, 5, 5, 5)

        # 1. Columna Izquierda: Búsqueda y Lista de Registros (similar a la captura)
        left_col = QVBoxLayout()
        left_col.setSpacing(5)
        left_col.addWidget(QLabel("Búsqueda:"))
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("Título, plataforma o género...")
        self.search.textChanged.connect(self.load_data)
        left_col.addWidget(self.search)

        left_col.addWidget(QLabel("Registros de Productos:"))
        self.list_widget = QListWidget() 
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.currentRowChanged.connect(self.update_detail_view)
        left_col.addWidget(self.list_widget)
        
        left_container = QWidget()
        left_container.setLayout(left_col)
        left_container.setFixedWidth(250)
        main_hlayout.addWidget(left_container)


        # 2. Columna Central: Detalles del Registro + Imagen
        center_col = QVBoxLayout()
        
        top_details_hlayout = QHBoxLayout()

        # GroupBox para Detalles (simulando Datos Generales)
        self.detail_group = QGroupBox("Detalles del Producto")
        detail_form = QFormLayout()
        
        # Campos de solo lectura (usaremos QLabels para mostrar los detalles)
        self.lbl_id = QLabel()
        self.lbl_title = QLabel()
        self.lbl_platform = QLabel()
        self.lbl_genre = QLabel()
        self.lbl_price = QLabel()
        self.lbl_stock = QLabel()
        
        detail_form.addRow("ID:", self.lbl_id)
        detail_form.addRow("Título:", self.lbl_title)
        detail_form.addRow("Plataforma:", self.lbl_platform)
        detail_form.addRow("Género:", self.lbl_genre)
        detail_form.addRow("Precio:", self.lbl_price)
        detail_form.addRow("Stock:", self.lbl_stock)
        self.detail_group.setLayout(detail_form)
        top_details_hlayout.addWidget(self.detail_group, 3) 

        # Previsualización de Imagen (simulando Foto del Empleado)
        self.preview = QLabel("Imagen")
        self.preview.setObjectName("previewBox")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedSize(200, 200) 
        top_details_hlayout.addWidget(self.preview, 1) 

        center_col.addLayout(top_details_hlayout)
        
        # Descripción (Toma el espacio restante)
        self.description_box = QGroupBox("Descripción")
        desc_vbox = QVBoxLayout()
        self.lbl_description = QTextEdit()
        self.lbl_description.setReadOnly(True)
        desc_vbox.addWidget(self.lbl_description)
        self.description_box.setLayout(desc_vbox)
        center_col.addWidget(self.description_box, 1)

        main_hlayout.addLayout(center_col, 1) 


        # 3. Columna Derecha: Botones de Acción (Panel de Acciones CRUD)
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        
        # Botones CRUD y Reporte
        btn_new = QPushButton("Agregar nuevo")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Eliminar")
        btn_print = QPushButton("Reporte de impresión")
        
        right_col.addWidget(btn_new)
        right_col.addWidget(btn_edit)
        right_col.addSpacing(20)
        right_col.addStretch(1) 
        right_col.addWidget(btn_del)
        right_col.addWidget(btn_print)
        
        btn_new.clicked.connect(self.on_new)
        btn_edit.clicked.connect(self.on_edit)
        btn_del.clicked.connect(self.on_delete)
        btn_print.clicked.connect(self.on_print_preview)
        
        right_container = QWidget()
        right_container.setLayout(right_col)
        right_container.setFixedWidth(180) 
        main_hlayout.addWidget(right_container)

        self.products_data = {} 
        
        db.init_db()
        self.load_data()
        self.update_detail_view() 

    # --- FUNCIÓN PARA ACTUALIZAR LA VISTA DE DETALLE ---
    def update_detail_view(self, current_row=None):
        idx = self.list_widget.currentRow()
        if idx < 0:
            for label in [self.lbl_id, self.lbl_title, self.lbl_platform, self.lbl_genre, self.lbl_price, self.lbl_stock]:
                label.setText("")
            self.lbl_description.setText("")
            self.preview.setText("Imagen")
            self.preview.setPixmap(QPixmap())
            return
            
        prod = self.products_data.get(idx)
        if not prod:
            return

        # Actualizar Etiquetas
        self.lbl_id.setText(str(prod.get("id", "")))
        self.lbl_title.setText(prod.get("title", ""))
        self.lbl_platform.setText(prod.get("platform", ""))
        self.lbl_genre.setText(prod.get("genre", ""))
        self.lbl_price.setText(human_price(prod.get("price") or 0))
        self.lbl_stock.setText(str(prod.get("stock") or 0))
        self.lbl_description.setText(prod.get("description", ""))

        # Actualizar Previsualización
        image_path = prod.get("image_path", "")
        if image_path and Path(image_path).exists():
            pix = QPixmap(image_path)
            if not pix.isNull():
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

    # --- MANEJO DE ACCIONES (CRUD) ---
    def on_new(self):
        dialog = ProductForm(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["title"] or not data["platform"]:
                QMessageBox.warning(
                    self, "Campos requeridos", "Título y Plataforma son obligatorios."
                )
                return
            if data["image_path"]:
                data["image_path"] = self._copy_to_media(data["image_path"])
            pid = db.insert_product(data)
            self.load_data(select_id=pid)

    def on_edit(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Editar Registro", "Seleccione un registro para editar.")
            return
            
        prod_data = self.products_data.get(idx)
        if not prod_data: return
        
        pid = prod_data.get("id")
        prod = db.get_product(pid)
        dialog = ProductForm(self, prod)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            if new_data["image_path"] and Path(new_data["image_path"]).resolve().parent != MEDIA_DIR.resolve():
                new_data["image_path"] = self._copy_to_media(new_data["image_path"])
            db.update_product(pid, new_data)
            self.load_data(select_id=pid)

    def on_delete(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Eliminar Registro", "Seleccione un registro para eliminar.")
            return
            
        prod_data = self.products_data.get(idx)
        if not prod_data: return
        
        pid = prod_data.get("id")
        title = prod_data.get("title", "Producto Desconocido")
        
        if QMessageBox.question(self, "Confirmar Eliminación", f"¿Eliminar el registro para '{title}' (ID: {pid})?") == QMessageBox.Yes:
            db.delete_product(pid)
            self.load_data()

    def on_print_preview(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.information(
                self,
                "Reporte de impresión",
                "Selecciona un producto en la lista para imprimir su ficha (Reporte).",
            )
            return

        prod_data = self.products_data.get(idx)
        if not prod_data: return
        
        pid = prod_data.get("id")
        prod = db.get_product(pid)
        if not prod:
            QMessageBox.warning(
                self,
                "Error de DB",
                "No se pudo obtener la información del producto.",
            )
            return

        dlg = ProductPrintPreview(prod, self)
        dlg.exec()
        
    def _copy_to_media(self, src: str) -> str:
        src_path = Path(src)
        if not src_path.exists():
            return ""
        dst = MEDIA_DIR / src_path.name
        i = 1
        while dst.exists():
            dst = MEDIA_DIR / f"{src_path.stem}_{i}{src_path.suffix}"
            i += 1
        shutil.copyfile(src_path, dst)
        return str(dst)
        
    # --- Carga de datos a la lista lateral ---
    def load_data(self, *_args, select_id: Optional[int] = None):
        items = db.list_products(self.search.text().strip())
        self.list_widget.clear()
        self.products_data = {}
        
        selected_index = -1
        
        for idx, prod in enumerate(items):
            # Formato de nombre en la lista: "ID - Título"
            display_name = f"{prod.get('id')} - {prod.get('title', 'Sin Título')}"
            self.list_widget.addItem(display_name)
            self.products_data[idx] = prod 

            if select_id and prod["id"] == select_id:
                selected_index = idx

        if selected_index != -1:
            self.list_widget.setCurrentRow(selected_index)
        elif self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0) 
            
        self.update_detail_view()


def main():
    app = QApplication(sys.argv)

    # Aplicar estilo global retro (Matrix green)
    app.setStyleSheet(GLOBAL_STYLESHEET)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()