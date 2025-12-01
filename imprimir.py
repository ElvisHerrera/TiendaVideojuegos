# imprimir.py
# Lógica de impresión de la ficha del videojuego (Windows / Linux)

from typing import Dict, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QFont
from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtPrintSupport import QPrinter, QPrintDialog


# -----------------------------------------------
# COMMIT: Nueva función que permite dibujar texto
# con word-wrap y devuelve el nuevo valor de Y.
# Esto evita que las palabras se peguen o salgan del margen.
# -----------------------------------------------
def draw_wrapped_text(painter: QPainter, x: int, y: int, width: int, text: str, line_height: int) -> int:
    # COMMIT: Se calcula la altura real que ocupará el texto
    rect_height = painter.fontMetrics().boundingRect(
        0, 0, width, 2000, Qt.TextWordWrap, text
    ).height()

    # COMMIT: Se dibuja el texto con wrap activado
    painter.drawText(x, y, width, rect_height, Qt.TextWordWrap, text)

    # COMMIT: Se devuelve la siguiente posición Y con espacio extra
    return y + rect_height + line_height



def imprimir_ficha(game: Dict, parent: Optional[QWidget] = None) -> None:
    printer = QPrinter(QPrinter.HighResolution)
    dialog = QPrintDialog(printer, parent)
    dialog.setWindowTitle("Imprimir ficha de videojuego")

    if dialog.exec() != QDialog.Accepted:
        return

    painter = QPainter(printer)

    try:
        try:
            rect = printer.pageRect()
        except TypeError:
            rect = printer.pageRect(QPrinter.DevicePixel)

        margin = 100
        x = rect.left() + margin
        y = rect.top() + margin
        max_width = rect.width() - 2 * margin

        # --- TÍTULO ---

        title = str(game.get("title", "")).strip() or "Videojuego sin título"

        # -----------------------------------------------
        # COMMIT: Tamaño de fuente del título aumentado
        # para mejorar la legibilidad en la impresión.
        # -----------------------------------------------
        title_font = QFont("Helvetica", 26, QFont.Bold)
        painter.setFont(title_font)

        # -----------------------------------------------
        # COMMIT: Ahora el título se dibuja con word-wrap
        # usando la nueva función. Antes era drawText fijo.
        # -----------------------------------------------
        y = draw_wrapped_text(painter, x, y, max_width, title, 40)


        # --- CUERPO DEL TEXTO ---

        # COMMIT: Fuente del cuerpo más grande que antes.
        body_font = QFont("Helvetica", 16)
        painter.setFont(body_font)

        company = str(game.get("company", "")).strip()
        release_date = str(game.get("release_date", "")).strip()

        if company:
            # COMMIT: Texto de compañía usando word-wrap
            y = draw_wrapped_text(
                painter, x, y, max_width,
                f"Compañía: {company}", 25
            )

        if release_date:
            # COMMIT: Texto de fecha usando word-wrap
            y = draw_wrapped_text(
                painter, x, y, max_width,
                f"Fecha de lanzamiento: {release_date}", 25
            )

        y += 20


        # --- IMAGEN ---
        image_data = game.get("image_data")

        if image_data:
            pix = QPixmap()

            if isinstance(image_data, (bytes, bytearray)):
                pix.loadFromData(image_data)
            else:
                try:
                    pix.loadFromData(bytes(image_data))
                except Exception:
                    pix = QPixmap()

            if not pix.isNull():

                # -----------------------------------------------
                # COMMIT: Imagen escalada a solo 40% del espacio
                # para que no ocupe casi toda la hoja.
                # -----------------------------------------------
                max_height = int((rect.height() - y - margin) * 0.40)

                scaled = pix.scaled(
                    max_width,
                    max_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )

                painter.drawPixmap(x, y, scaled)

    finally:
        painter.end()
