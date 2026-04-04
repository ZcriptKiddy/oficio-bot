from flask import Flask, request, send_file
from docx import Document
import uuid

app = Flask(__name__)

def reemplazar(doc, data):
    for p in doc.paragraphs:
        for key, value in data.items():
            if f"{{{{{key}}}}}" in p.text:
                p.text = p.text.replace(f"{{{{{key}}}}}", value)

@app.route("/generar", methods=["POST"])
def generar():
    data = request.json

    doc = Document("plantilla.docx")
    reemplazar(doc, data)

    nombre_archivo = f"oficio_{uuid.uuid4()}.docx"
    doc.save(nombre_archivo)

    return send_file(nombre_archivo, as_attachment=True)

import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))