import os
import tempfile

import imprimir


def test_render_ficha_to_pdf_or_requires_reportlab():
    game = {
        "title": "Prueba PDF",
        "company": "ACME",
        "release_date": "2021-01-01",
        "image_data": None,
    }

    # If reportlab isn't available (A4 == None), the function should raise
    if getattr(imprimir, "A4", None) is None:
        try:
            imprimir.render_ficha_to_pdf(game, "/tmp/test.pdf")
        except RuntimeError:
            return
        raise AssertionError("Expected RuntimeError when reportlab is missing")

    # Otherwise it should create a PDF file
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        imprimir.render_ficha_to_pdf(game, path)
        assert os.path.exists(path) and os.path.getsize(path) > 0
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
