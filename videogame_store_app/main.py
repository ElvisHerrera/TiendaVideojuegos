import sys
import shutil
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QPixmap, QPainter
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
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

import db

APP_DIR = Path(__file__).resolve().parent
MEDIA_DIR = APP_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True)

PLATFORMS = ["PC", "PlayStation", "Xbox", "Nintendo", "Steam Deck", "Otro"]


def human_price(p: float) -> str:
    return f"${p:,.2f}"


class ProductForm(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Producto")
        self.setMinimumWidth(420)
        self.data = data or {}
        self.image_path = self.data.get("image_path")

        layout = QVBoxLayout(self)
        form = QFormLayout()

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
        self.img_preview.setStyleSheet("border:1px dashed #999; border-radius:10px;")
        if self.image_path and Path(self.image_path).exists():
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
            self.img_preview.setPixmap(
                pix.scaled(
                    self.img_preview.size(),
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
    """
    Vista previa tipo formulario:
    - Muestra los datos del producto y la imagen.
    - Botón Volver y botón Imprimir (usa el cuadro de impresión de Windows).
    """

    def __init__(self, product: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista previa de impresión - Ficha de producto")
        self.resize(800, 600)

        # Aseguramos que sea un dict "normal"
        if hasattr(product, "keys") and not isinstance(product, dict):
            try:
                self.product = {k: product[k] for k in product.keys()}
            except Exception:
                self.product = dict(product)
        else:
            self.product = dict(product or {})

        main_layout = QVBoxLayout(self)

        # Barra superior: Volver (izquierda) + Imprimir (derecha)
        top_bar = QHBoxLayout()
        btn_back = QPushButton("← Volver")
        btn_print = QPushButton("Imprimir")
        top_bar.addWidget(btn_back)
        top_bar.addStretch(1)
        top_bar.addWidget(btn_print)
        main_layout.addLayout(top_bar)

        # Contenido principal: izquierda datos, derecha imagen
        body = QHBoxLayout()
        main_layout.addLayout(body, 1)

        left = QVBoxLayout()
        right = QVBoxLayout()
        body.addLayout(left, 2)
        body.addLayout(right, 1)

        # Título grande
        self.lbl_title = QLabel()
        font = self.lbl_title.font()
        font.setPointSize(16)
        font.setBold(True)
        self.lbl_title.setFont(font)
        left.addWidget(self.lbl_title)

        # Datos en forma
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

        # Descripción
        lbl_desc_title = QLabel("Descripción:")
        self.txt_desc = QTextEdit()
        self.txt_desc.setReadOnly(True)
        self.txt_desc.setFixedHeight(180)
        left.addWidget(lbl_desc_title)
        left.addWidget(self.txt_desc, 1)

        # Imagen a la derecha
        self.img_label = QLabel("Sin imagen")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("border:1px solid #ccc; border-radius:8px;")
        right.addWidget(self.img_label, 1)

        # Rellenar datos
        self._fill_from_product()

        btn_back.clicked.connect(self.reject)
        btn_print.clicked.connect(self._print)

    def _fill_from_product(self):
        p = self.product

        title = p.get("title", "")
        platform = p.get("platform", "")
        genre = p.get("genre", "")
        price = p.get("price") or 0
        stock = p.get("stock") or 0
        desc = p.get("description", "")
        img_path = p.get("image_path", "") or ""

        self.lbl_title.setText(title)
        self.lbl_platform.setText(platform)
        self.lbl_genre.setText(genre)
        self.lbl_price.setText(human_price(float(price)))
        self.lbl_stock.setText(f"{int(stock)} unidades")
        self.txt_desc.setPlainText(desc)

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
            # Capturamos el contenido del diálogo como imagen
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
        self.setWindowTitle("Tienda de Videojuegos - CRUD + Impresión")
        self.resize(1100, 650)

        # Toolbar & actions
        toolbar = QToolBar("Main")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        act_new = QAction("Nuevo", self)
        act_edit = QAction("Editar", self)
        act_del = QAction("Eliminar", self)
        act_print = QAction("Vista previa de impresión", self)

        act_new.triggered.connect(self.on_new)
        act_edit.triggered.connect(self.on_edit)
        act_del.triggered.connect(self.on_delete)
        act_print.triggered.connect(self.on_print_preview)

        toolbar.addAction(act_new)
        toolbar.addAction(act_edit)
        toolbar.addAction(act_del)
        toolbar.addSeparator()
        toolbar.addAction(act_print)

        # Search box
        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Buscar por título, plataforma o género..."
        )
        self.search.textChanged.connect(self.load_data)
        toolbar.addSeparator()
        toolbar.addWidget(self.search)

        # Central UI
        central = QWidget()
        self.setCentralWidget(central)

        splitter = QSplitter()
        left = QWidget()
        right = QWidget()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([700, 400])

        lay = QHBoxLayout(central)
        lay.addWidget(splitter)

        # Left: table
        vleft = QVBoxLayout(left)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Título", "Plataforma", "Género", "Precio", "Stock", "Imagen"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit)
        self.table.setColumnHidden(0, False)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 70)
        self.table.setColumnWidth(6, 160)
        vleft.addWidget(self.table)

        # Right: image preview
        vright = QVBoxLayout(right)
        self.preview = QLabel("Previsualización de imagen")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("border:1px solid #ccc; border-radius:8px;")
        vright.addWidget(self.preview)

        # events
        self.table.itemSelectionChanged.connect(self.update_preview)

        # init
        db.init_db()
        self.load_data()

    # CRUD
    def on_new(self):
        dialog = ProductForm(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["title"] or not data["platform"]:
                QMessageBox.warning(
                    self,
                    "Campos requeridos",
                    "Título y Plataforma son obligatorios.",
                )
                return
            # copy image
            if data["image_path"]:
                data["image_path"] = self._copy_to_media(data["image_path"])
            pid = db.insert_product(data)
            self.load_data(select_id=pid)

    def on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Editar", "Seleccione un registro.")
            return
        pid = int(self.table.item(row, 0).text())
        prod = db.get_product(pid)
        dialog = ProductForm(self, prod)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            # If image path is external, copy into media
            if new_data["image_path"] and Path(
                new_data["image_path"]
            ).resolve().parent != MEDIA_DIR.resolve():
                new_data["image_path"] = self._copy_to_media(
                    new_data["image_path"]
                )
            db.update_product(pid, new_data)
            self.load_data(select_id=pid)

    def on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Eliminar", "Seleccione un registro.")
            return
        pid = int(self.table.item(row, 0).text())
        title = self.table.item(row, 1).text()
        if (
            QMessageBox.question(
                self, "Confirmar", f"¿Eliminar '{title}'?"
            )
            == QMessageBox.Yes
        ):
            db.delete_product(pid)
            self.load_data()

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

    def load_data(self, *_args, select_id: Optional[int] = None):
        items = db.list_products(self.search.text().strip())
        self.table.setRowCount(0)
        for prod in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(prod["id"])))
            self.table.setItem(
                row, 1, QTableWidgetItem(prod.get("title", ""))
            )
            self.table.setItem(
                row, 2, QTableWidgetItem(prod.get("platform", ""))
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(prod.get("genre", ""))
            )
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(human_price(prod.get("price") or 0)),
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(str(prod.get("stock") or 0))
            )

            # Columna imagen: nombre.ext y ruta real en UserRole
            img_path = prod.get("image_path", "") or ""
            display_name = Path(img_path).name if img_path else ""
            img_text = display_name if display_name else "Sin imagen"
            img_item = QTableWidgetItem(img_text)
            img_item.setData(Qt.UserRole, img_path)
            self.table.setItem(row, 6, img_item)

        if select_id:
            for r in range(self.table.rowCount()):
                if int(self.table.item(r, 0).text()) == select_id:
                    self.table.selectRow(r)
                    break
        self.update_preview()

    def update_preview(self):
        row = self.table.currentRow()
        if row < 0:
            self.preview.setText("Previsualización de imagen")
            self.preview.setPixmap(QPixmap())
            return
        image_path_item = self.table.item(row, 6)
        image_path = (
            image_path_item.data(Qt.UserRole) if image_path_item else ""
        )
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

    # --- Vista previa de impresión: ficha de producto ---
    def on_print_preview(self):
        # Fila seleccionada en la tabla
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "Vista previa de impresión",
                "Selecciona un producto en la tabla para imprimir su ficha.",
            )
            return

        pid = int(self.table.item(row, 0).text())
        prod = db.get_product(pid)
        if not prod:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo obtener la información del producto.",
            )
            return

        dlg = ProductPrintPreview(prod, self)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
