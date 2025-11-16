import sys
import shutil
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QAction, QPixmap, QPainter, QTextOption
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QLineEdit, QDialog,
    QFormLayout, QDialogButtonBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QMessageBox, QToolBar, QSplitter
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

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
        self.price.setRange(0, 9999999)
        self.price.setDecimals(2)
        self.price.setValue(float(self.data.get("price", 0)))
        self.stock = QSpinBox()
        self.stock.setRange(0, 999999)
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
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", str(Path.home()), "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)")
        if path:
            self.image_path = path
            self._load_preview(path)

    def _load_preview(self, path):
        pix = QPixmap(path)
        if not pix.isNull():
            self.img_preview.setPixmap(pix.scaled(self.img_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.img_preview.setText("Imagen no válida")

    def get_data(self):
        return {
            "title": self.title.text().strip(),
            "platform": self.platform.currentText(),
            "genre": self.genre.text().strip(),
            "price": float(self.price.value()),
            "stock": int(self.stock.value()),
            "description": self.description.toPlainText().strip(),
            "image_path": self.image_path
        }

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
        self.search.setPlaceholderText("Buscar por título, plataforma o género...")
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
        self.table.setHorizontalHeaderLabels(["ID", "Título", "Plataforma", "Género", "Precio", "Stock", "Imagen"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit)
        self.table.setColumnHidden(0, False)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 70)
        self.table.setColumnWidth(6, 260)
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
                QMessageBox.warning(self, "Campos requeridos", "Título y Plataforma son obligatorios.")
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
            if new_data["image_path"] and Path(new_data["image_path"]).resolve().parent != MEDIA_DIR.resolve():
                new_data["image_path"] = self._copy_to_media(new_data["image_path"])
            db.update_product(pid, new_data)
            self.load_data(select_id=pid)

    def on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Eliminar", "Seleccione un registro.")
            return
        pid = int(self.table.item(row, 0).text())
        title = self.table.item(row, 1).text()
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar '{title}'?") == QMessageBox.Yes:
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
            self.table.setItem(row, 1, QTableWidgetItem(prod.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(prod.get("platform", "")))
            self.table.setItem(row, 3, QTableWidgetItem(prod.get("genre", "")))
            self.table.setItem(row, 4, QTableWidgetItem(human_price(prod.get("price") or 0)))
            self.table.setItem(row, 5, QTableWidgetItem(str(prod.get("stock") or 0)))
            self.table.setItem(row, 6, QTableWidgetItem(prod.get("image_path", "")))

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
        image_path = image_path_item.text() if image_path_item else ""
        if image_path and Path(image_path).exists():
            pix = QPixmap(image_path)
            if not pix.isNull():
                self.preview.setPixmap(pix.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.preview.setText("Imagen no válida")
        else:
            self.preview.setText("Sin imagen")

    # Print simulation
    def on_print_preview(self):
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        dlg.setWindowTitle("Seleccionar impresora (simulación)")
        if dlg.exec() != QDialog.Accepted:
            return
        preview = QPrintPreviewDialog(printer, self)
        preview.setWindowTitle("Vista previa de impresión - Catálogo")
        preview.paintRequested.connect(self._render_catalog_on_printer)
        preview.exec()

    def _render_catalog_on_printer(self, printer: QPrinter):
        painter = QPainter(printer)
        try:
            margin = 20
            page_rect = printer.pageRect()
            x, y = margin, margin
            card_w = 230
            card_h = 220
            gap = 12

            cols = max(1, (page_rect.width() - 2*margin + gap) // (card_w + gap))

            items = db.list_products(self.search.text().strip())
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)

            for idx, prod in enumerate(items):
                if y + card_h > page_rect.bottom() - margin:
                    printer.newPage()
                    x, y = margin, margin

                rect = QRectF(x, y, card_w, card_h)
                painter.drawRect(rect)

                img_rect = QRectF(x + 8, y + 8, card_w - 16, card_h - 70)
                path = prod.get("image_path") or ""
                pix = QPixmap(path) if path and Path(path).exists() else QPixmap()
                if not pix.isNull():
                    scaled = pix.scaled(img_rect.size().toSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    ix = x + (card_w - scaled.width())/2
                    iy = y + 8 + (img_rect.height() - scaled.height())/2
                    painter.drawPixmap(int(ix), int(iy), scaled)
                else:
                    painter.drawText(img_rect, Qt.AlignCenter, "Sin imagen")

                title_rect = QRectF(x + 8, y + card_h - 56, card_w - 16, 36)
                opt = QTextOption(Qt.AlignHCenter | Qt.AlignTop)
                opt.setWrapMode(QTextOption.WordWrap)
                painter.drawText(title_rect, prod.get("title", "S/T"), opt)

                price_rect = QRectF(x + 8, y + card_h - 20, card_w - 16, 16)
                painter.drawText(price_rect, Qt.AlignCenter, f"{prod.get('platform','')} · {prod.get('genre','')} · {human_price(prod.get('price') or 0)}")

                col_index = (idx % cols)
                if col_index == cols - 1:
                    x = margin
                    y += card_h + gap
                else:
                    x += card_w + gap
        finally:
            painter.end()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
