"""Small HTTP service that accepts print requests and sends them to the
local system printer.

Usage: python3 print_server.py

Endpoints:
 - GET /health
 - POST /print/raw  -> JSON payload with keys: title, company, release_date, image_data (base64)
 - POST /print/id/<id> -> print by videogame id fetched from DB

The server will render the provided game data to a PDF and send it to the
system printer using the helpers in `imprimir.py`.
"""
import base64
import json
import os
import tempfile
from typing import Optional

from flask import Flask, jsonify, request

import db
import imprimir


app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def _parse_game_from_json(data: dict) -> dict:
    image_b64 = data.get("image_data")
    image_bytes = None
    if image_b64:
        try:
            image_bytes = base64.b64decode(image_b64)
        except Exception:
            image_bytes = None

    return {
        "title": data.get("title"),
        "company": data.get("company"),
        "release_date": data.get("release_date"),
        "image_data": image_bytes,
    }


@app.route("/print/raw", methods=["POST"])
def print_raw():
    payload = request.get_json() or {}
    if not payload.get("title"):
        return jsonify({"error": "missing title"}), 400

    game = _parse_game_from_json(payload)

    # Optional printer name can be passed as query param or JSON field
    printer_name = request.args.get("printer") or payload.get("printer_name")

    try:
        fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        imprimir.render_ficha_to_pdf(game, tmp_pdf)
        imprimir.send_pdf_to_printer(tmp_pdf, printer_name)
        # don't remove the pdf immediately: leave it for debugging if needed
        return jsonify({"status": "printed", "pdf": tmp_pdf})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/preview/raw", methods=["POST"])
def preview_raw():
    payload = request.get_json() or {}
    if not payload.get("title"):
        return jsonify({"error": "missing title"}), 400

    game = _parse_game_from_json(payload)

    try:
        fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        imprimir.render_ficha_to_pdf(game, tmp_pdf)
        # Serve the PDF for inline preview
        from flask import send_file

        return send_file(tmp_pdf, mimetype="application/pdf", as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/preview/id/<int:pid>", methods=["GET"])
def preview_by_id(pid: int):
    game = db.get_product(pid)
    if not game:
        return jsonify({"error": "not found"}), 404

    try:
        fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        imprimir.render_ficha_to_pdf(game, tmp_pdf)
        from flask import send_file

        return send_file(tmp_pdf, mimetype="application/pdf", as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/print/id/<int:pid>", methods=["POST"])
def print_by_id(pid: int):
    printer_name = request.args.get("printer")
    game = db.get_product(pid)
    if not game:
        return jsonify({"error": "not found"}), 404

    try:
        fd, tmp_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        imprimir.render_ficha_to_pdf(game, tmp_pdf)
        imprimir.send_pdf_to_printer(tmp_pdf, printer_name)
        return jsonify({"status": "printed", "pdf": tmp_pdf})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    port = int(os.getenv("PRINT_SERVER_PORT", "5000"))
    host = os.getenv("PRINT_SERVER_HOST", "0.0.0.0")
    # Only for development / local server. For production use system service
    # and a process manager.
    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
