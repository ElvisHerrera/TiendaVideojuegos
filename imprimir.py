# imprimir.py
# Lógica de impresión de la ficha del videojuego (Windows / Linux)

from typing import Dict, Optional
import base64
import io
import os
import sys
import subprocess
import tempfile

# reportlab is used to render a PDF on the server side (no GUI required)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except Exception:
    # reportlab may not be installed in lightweight test environments
    A4 = None
try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPainter, QPixmap, QFont
    from PySide6.QtWidgets import QWidget, QDialog
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
    _HAS_QT = True
except Exception:
    # Allow importing this module in environments without PySide6 (tests, CI)
    Qt = None
    QPainter = None
    QPixmap = None
    QFont = None
    QWidget = None
    QDialog = None
    QPrinter = None
    QPrintDialog = None
    _HAS_QT = False


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
    if not _HAS_QT:
        raise RuntimeError("PySide6 is required for local GUI printing (imprimir_ficha)")

    # Use print preview dialog so the user can preview and then choose "Print".
    printer = QPrinter(QPrinter.HighResolution)
    preview = QPrintPreviewDialog(printer, parent)

    def _paint(pr: QPrinter):
        painter = QPainter(pr)
        try:
            try:
                rect = pr.pageRect()
            except TypeError:
                rect = pr.pageRect(QPrinter.DevicePixel)

            margin = 100
            x = rect.left() + margin
            y = rect.top() + margin
            max_width = rect.width() - 2 * margin

            # --- TÍTULO ---
            title = str(game.get("title", "")).strip() or "Videojuego sin título"

            title_font = QFont("Helvetica", 26, QFont.Bold)
            painter.setFont(title_font)

            y = draw_wrapped_text(painter, x, y, max_width, title, 40)

            # --- CUERPO DEL TEXTO ---
            body_font = QFont("Helvetica", 16)
            painter.setFont(body_font)

            company = str(game.get("company", "")).strip()
            release_date = str(game.get("release_date", "")).strip()

            if company:
                y = draw_wrapped_text(painter, x, y, max_width, f"Compañía: {company}", 25)

            if release_date:
                y = draw_wrapped_text(painter, x, y, max_width, f"Fecha de lanzamiento: {release_date}", 25)

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
                    max_height = int((rect.height() - y - margin) * 0.40)
                    scaled = pix.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    painter.drawPixmap(x, y, scaled)
        finally:
            painter.end()

    preview.paintRequested.connect(_paint)
    preview.setWindowTitle("Vista previa - Ficha de videojuego")
    # Execute the preview dialog: user can inspect and choose Print in the dialog
    if preview.exec() != QDialog.Accepted:
        # Preview canceled by user
        return
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

    # If the user accepted the preview dialog and clicked Print, the
    # QPrintPreviewDialog will have already handled the printing via the
    # chosen QPrinter.


def render_ficha_to_pdf(game: Dict, output_path: str) -> None:
    """Renderiza la ficha del videojuego a un PDF usando reportlab.

    - game: diccionario que contiene 'title', 'company', 'release_date' y 'image_data' (bytes)
    - output_path: ruta del archivo PDF a generar
    """
    if A4 is None:
        raise RuntimeError("reportlab library is required to render PDFs. Install reportlab in your environment.")

    width, height = A4
    c = canvas.Canvas(output_path, pagesize=A4)

    margin = 50
    x = margin
    y = height - margin

    title = str(game.get("title", "")).strip() or "Videojuego sin título"
    company = str(game.get("company", "")).strip()
    release_date = str(game.get("release_date", "")).strip()

    # Título
    c.setFont("Helvetica-Bold", 26)
    c.drawString(x, y, title)
    y -= 40

    # Cuerpo
    c.setFont("Helvetica", 14)
    if company:
        c.drawString(x, y, f"Compañía: {company}")
        y -= 24
    if release_date:
        c.drawString(x, y, f"Fecha de lanzamiento: {release_date}")
        y -= 30

    # Imagen (si existe)
    image_data = game.get("image_data")
    if image_data:
        try:
            # ImageReader acepta bytes-like objects via io.BytesIO
            img = ImageReader(io.BytesIO(image_data))

            # Intenta dibujar la imagen ocupando hasta cierto espacio
            max_w = width - 2 * margin
            max_h = y - margin

            iw, ih = img.getSize()
            scale = min(max_w / iw, max_h / ih, 1.0)
            draw_w = iw * scale
            draw_h = ih * scale

            c.drawImage(img, x, y - draw_h, width=draw_w, height=draw_h)
            y -= draw_h + 10
        except Exception:
            # si la imagen falla, se ignora y se continúa
            pass

    c.showPage()
    c.save()


def send_pdf_to_printer(pdf_path: str, printer_name: Optional[str] = None) -> None:
    """Envía un PDF a la impresora del sistema.

    - En Linux/Unix se usa `lp` (CUPS). Si printer_name se especifica, se usa `-d`.
    - En Windows intenta usar pywin32 (win32print) si está disponible; si no, usa os.startfile(..., 'print')
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    platform = sys.platform

    # Linux / macOS path: lp
    if platform.startswith("linux") or platform.startswith("darwin"):
        cmd = ["lp"]
        if printer_name:
            cmd += ["-d", printer_name]
        cmd.append(pdf_path)
        subprocess.run(cmd, check=True)
        return

    # Windows
    if platform.startswith("win"):
        try:
            import win32print  # type: ignore
            import win32api  # type: ignore

            # If printer_name provided, open it; otherwise use default
            if printer_name:
                hPrinter = win32print.OpenPrinter(printer_name)
            else:
                hPrinter = win32print.OpenPrinter(win32print.GetDefaultPrinter())

            # Use ShellExecute for printing - many apps will honor the 'print' verb
            win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
            win32print.ClosePrinter(hPrinter)
            return
        except Exception:
            # fallback - rely on os.startfile which uses file associations
            try:
                os.startfile(pdf_path, "print")  # type: ignore
                return
            except Exception as e:
                raise RuntimeError(f"No se pudo enviar a la impresora en Windows: {e}")

    raise RuntimeError(f"Plataforma no soportada para envío directo a impresora: {platform}")


def print_game_to_system_printer(game: Dict, printer_name: Optional[str] = None) -> str:
    """Conveniencia: renderiza a PDF en un archivo temporal y lo envía a la impresora.

    Devuelve la ruta al PDF temporal generado.
    """
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        render_ficha_to_pdf(game, path)
        send_pdf_to_printer(path, printer_name)
        return path
    except Exception:
        # en caso de error, intentar limpiar y volver a propagar
        try:
            os.remove(path)
        except Exception:
            pass
        raise


def imprimir_via_servidor(server_url: str, game: Dict) -> bool:
    """Envia la ficha (con imagen) al servidor de impresión. server_url debe apuntar
    al endpoint /print/raw como por ejemplo http://print-server:5000/print/raw
    """
    import json
    import requests

    payload = {
        "title": game.get("title"),
        "company": game.get("company"),
        "release_date": game.get("release_date"),
        # image as base64 string if exists
        "image_data": base64.b64encode(game.get("image_data", b""))
        .decode("ascii")
        if game.get("image_data")
        else None,
    }

    r = requests.post(server_url.rstrip("/") + "/print/raw", json=payload, timeout=30)
    return r.status_code == 200
