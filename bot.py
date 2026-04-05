from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests

TOKEN = "8714423107:AAFxzv29AGjWaDUIS5iSID-hwTkn2gNQTxM"

datos_usuario = {}

async def oficio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datos_usuario[update.effective_user.id] = {}
    await update.message.reply_text("Dame número de carpeta:")

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

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    agencia = query.data
    data = datos_usuario.get(user_id, {})
    data["agencia"] = agencia
    await query.edit_message_text("Generando documento...")
    response = requests.post(
        "https://oficio-api.onrender.com/generar",
        json=data,
        timeout=60
    )
    if response.status_code != 200:
        await query.message.reply_text("Error al generar el documento.")
        return
    with open("resultado.docx", "wb") as f:
        f.write(response.content)
    await query.message.reply_document(open("resultado.docx", "rb"))
    datos_usuario[user_id] = {}

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("oficio", oficio))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))
app.add_handler(CallbackQueryHandler(botones))

app.run_polling()