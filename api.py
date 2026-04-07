from flask import Flask, request, send_file, jsonify
from docx import Document
import uuid
import os

app = Flask(__name__)

# 🔁 Función mejorada: reemplaza texto en párrafos y tablas
def reemplazar(doc, data):
    # Reemplazar en párrafos normales
    for p in doc.paragraphs:
        for key, value in data.items():
            if f"{{{{{key}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{key}}}}}", str(value))

    # Reemplazar en tablas (MUY IMPORTANTE)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in data.items():
                    if f"{{{{{key}}}}}" in cell.text:
                        cell.text = cell.text.replace(f"{{{{{key}}}}}", str(value))


@app.route("/")
def home():
    return "API activa"


# 📄 Endpoint principal
@app.route("/generar", methods=["POST"])
def generar():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # 📂 Cargar plantilla
        doc = Document("plantilla.docx")

        # 🔁 Reemplazar datos
        reemplazar(doc, data)

        # 📄 Crear nombre único
        nombre_archivo = f"oficio_{uuid.uuid4()}.docx"
        doc.save(nombre_archivo)

        # 📤 Enviar archivo
        return send_file(nombre_archivo, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))