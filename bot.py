from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests
import threading
import time
from flask import Flask

TOKEN = "8714423107:AAFxzv29AGjWaDUIS5iSID-hwTkn2gNQTxM"

# 🔄 ==============================
# CAMBIO DE MODO
# ==============================
MODO = "PRODUCTION"   # 🔁 Cambiar a "LOCAL" cuando pruebes en tu PC

if MODO == "LOCAL":
    API_URL = "http://127.0.0.1:5000"
else:
    API_URL = "https://oficio-api.onrender.com"

datos_usuario = {}

# 🔄 FUNCIÓN PARA DESPERTAR API
def despertar_api():
    try:
        for intento in range(10):
            try:
                r = requests.get(API_URL, timeout=5)
                if r.status_code == 200:
                    return True
            except:
                pass
            time.sleep(2)
        return False
    except:
        return False


# 🚀 Comando inicial
async def oficio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    datos_usuario[user_id] = {}

    # ⏳ Mensaje inicial
    mensaje = await update.message.reply_text("⏳ Preparando sistema, espera...")

    # 🔄 Wake-up (solo útil en PROD pero no estorba en LOCAL)
    ok = despertar_api()

    if not ok:
        await mensaje.edit_text("❌ No se pudo iniciar el servicio. Intenta nuevamente.")
        return

    await mensaje.edit_text("✅ Sistema listo.\n\nDame número de carpeta:")


# 💬 Captura de datos
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


# 🔘 Botones
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    agencia = query.data
    data = datos_usuario.get(user_id, {})
    data["agencia"] = agencia

    await query.edit_message_text("⏳ Generando documento...")

    try:
        response = requests.post(
            f"{API_URL}/generar",
            json=data,
            timeout=90
        )

        if response.status_code != 200:
            await query.message.reply_text("❌ Error al generar documento.")
            return

        # 📄 Guardar temporal
        with open("resultado.docx", "wb") as f:
            f.write(response.content)

        # 📤 Enviar
        await query.message.reply_document(open("resultado.docx", "rb"))

    except requests.exceptions.Timeout:
        await query.message.reply_text("⏱️ El servidor tardó demasiado.")

    except requests.exceptions.ConnectionError:
        await query.message.reply_text("🌐 Error de conexión.")

    except Exception as e:
        await query.message.reply_text(f"❌ Error inesperado: {str(e)}")

    finally:
        datos_usuario[user_id] = {}


# 🤖 BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("oficio", oficio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))
app.add_handler(CallbackQueryHandler(botones))


# 🌐 Web para Render (mantener vivo)
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot activo"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)


# 🔄 Ejecutar web en paralelo (solo útil en Render)
threading.Thread(target=run_web).start()


# ▶️ Ejecutar bot
app.run_polling()