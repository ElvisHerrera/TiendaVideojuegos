# imprimir.py
# Lógica de impresión de la ficha del videojuego (Windows / Linux)
from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QFont
from PySide6.QtWidgets import QWidget, QMessageBox, QDialog
from PySide6.QtPrintSupport import QPrinter, QPrintDialog


def imprimir_ficha(game: Dict, parent: Optional[QWidget] = None) -> None:
    """
    Imprime la ficha del videojuego recibido en 'game'.

    Keys esperadas en game:
      - title         (str)
      - company       (str)
      - release_date  (str o date)
      - image_data    (bytes, opcional)

    Funciona tanto en Windows como en Linux, porque QPrinter/QPrintDialog
    usan el sistema de impresión nativo (spooler / CUPS).
    """
    # 1) Seleccionar impresora
    printer = QPrinter(QPrinter.HighResolution)

    dialog = QPrintDialog(printer, parent)
    dialog.setWindowTitle("Imprimir ficha de videojuego")

    if dialog.exec() != QDialog.Accepted:
        # Usuario canceló
        return

    # 2) Empezar a pintar la página
    painter = QPainter(printer)

    try:
        rect = printer.pageRect()  # área útil de la página
        margin = 80  # margen en unidades del dispositivo

        x = rect.left() + margin
        y = rect.top() + margin
        max_width = rect.width() - 2 * margin

        # ---- Cabecera: título del juego ----
        title = str(game.get("title", "")).strip() or "Videojuego sin título"
        company = str(game.get("company", "")).strip()
        release_date = str(game.get("release_date", "")).strip()

        title_font = QFont("Helvetica", 18, QFont.Bold)
        painter.setFont(title_font)

        # Dibujamos el título ocupando el ancho disponible
        painter.drawText(
            x,
            y,
            max_width,
            40,
            Qt.AlignLeft | Qt.AlignVCenter,
            title,
        )
        y += 50  # espacio después del título

        # ---- Detalles (texto) ----
        body_font = QFont("Helvetica", 11)
        painter.setFont(body_font)

        lines = []
        if company:
            lines.append(f"Compañía: {company}")
        if release_date:
            lines.append(f"Fecha de lanzamiento: {release_date}")

        for line in lines:
            painter.drawText(
                x,
                y,
                max_width,
                20,
                Qt.AlignLeft | Qt.AlignVCenter,
                line,
            )
            y += 25

        # Un poco de espacio antes de la imagen
        y += 20

        # ---- Imagen (opcional) ----
        image_data = game.get("image_data")

        if image_data:
            pix = QPixmap()

            # image_data normalmente viene como bytes desde PostgreSQL
            if isinstance(image_data, (bytes, bytearray)):
                pix.loadFromData(image_data)
            else:
                # Si por algún motivo llega una ruta o algo raro
                try:
                    pix.loadFromData(bytes(image_data))
                except Exception:
                    pix = QPixmap()

            if not pix.isNull():
                max_height = rect.height() - y - margin

                scaled = pix.scaled(
                    max_width,
                    max_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )

                painter.drawPixmap(x, y, scaled)
        # Si no hay imagen, simplemente no se dibuja nada adicional

    finally:
        painter.end()
