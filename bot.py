from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests
import threading
import time
from flask import Flask

TOKEN = "TU_TOKEN_AQUI"

# 🌐 URL de tu API en Render
API_URL = "https://oficio-api.onrender.com"

datos_usuario = {}

# 🔄 FUNCIÓN PARA DESPERTAR LA API
def despertar_api():
    try:
        for intento in range(10):  # intenta varias veces
            try:
                r = requests.get(API_URL, timeout=5)
                if r.status_code == 200:
                    return True
            except:
                pass
            time.sleep(2)  # espera antes de reintentar
        return False
    except:
        return False


# 🚀 Comando /oficio
async def oficio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    datos_usuario[user_id] = {}

    # ⏳ Mensaje de espera
    mensaje = await update.message.reply_text("⏳ Preparando sistema, espera unos segundos...")

    # 🔄 Despertar API
    ok = despertar_api()

    if not ok:
        await mensaje.edit_text("❌ No se pudo iniciar el servicio. Intenta nuevamente.")
        return

    await mensaje.edit_text("✅ Sistema listo.\n\nDame número de carpeta:")


# 💬 Manejo de mensajes
async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text

    data = datos_usuario.get(user_id, {})

    if "carpeta" not in data:
        data["carpeta"] = texto
        await update.message.reply_text("Describe el indicio:")

    elif "descripcion" not in data:
        data["descripcion"] = texto

        teclado = [
            [InlineKeyboardButton("1", callback_data="1"),
             InlineKeyboardButton("2", callback_data="2"),
             InlineKeyboardButton("3", callback_data="3")],
            [InlineKeyboardButton("4", callback_data="4"),
             InlineKeyboardButton("5", callback_data="5"),
             InlineKeyboardButton("6", callback_data="6")],
            [InlineKeyboardButton("7", callback_data="7"),
             InlineKeyboardButton("8", callback_data="8"),
             InlineKeyboardButton("9", callback_data="9")],
            [InlineKeyboardButton("10", callback_data="10")],
            [InlineKeyboardButton("Especializadas", callback_data="Especializadas")]
        ]

        await update.message.reply_text(
            "Selecciona agencia:",
            reply_markup=InlineKeyboardMarkup(teclado)
        )


# 🔘 Manejo de botones
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    agencia = query.data
    data = datos_usuario.get(user_id, {})
    data["agencia"] = agencia

    await query.edit_message_text("⏳ Generando documento, espera...")

    try:
        # 📤 Enviar datos a la API
        response = requests.post(
            f"{API_URL}/generar",
            json=data,
            timeout=90  # más tiempo por si despierta
        )

        if response.status_code != 200:
            await query.message.reply_text("❌ Error al generar documento.")
            return

        # 📄 Guardar archivo temporal
        with open("resultado.docx", "wb") as f:
            f.write(response.content)

        # 📤 Enviar al usuario
        await query.message.reply_document(open("resultado.docx", "rb"))

    except requests.exceptions.Timeout:
        await query.message.reply_text("⏱️ El servidor tardó demasiado. Intenta de nuevo.")

    except requests.exceptions.ConnectionError:
        await query.message.reply_text("🌐 Error de conexión con la API.")

    except Exception as e:
        await query.message.reply_text(f"❌ Error inesperado: {str(e)}")

    finally:
        datos_usuario[user_id] = {}


# 🤖 Configuración del bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("oficio", oficio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))
app.add_handler(CallbackQueryHandler(botones))


# 🌐 Web para mantener activo Render
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot activo"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

# 🔄 Ejecutar Flask en paralelo
threading.Thread(target=run_web).start()

# ▶️ Ejecutar bot
app.run_polling()