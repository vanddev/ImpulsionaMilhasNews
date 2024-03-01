import asyncio
import json
import os
from typing import Tuple

from quart import Quart, request
from retry import retry
import logging
import firebase as db

from telegram import Update
from telegram.error import NetworkError
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

app = Quart(__name__)

TOKEN = os.getenv('BOT_TOKEN', '')
WEBHOOK = os.getenv('WEBHOOK_URL', '')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger('quart.app')
application = (Application.builder().token(TOKEN).read_timeout(10)
               .write_timeout(10).connect_timeout(10).pool_timeout(10).build())


@retry(NetworkError, tries=3)
async def prev_ultima_promocao(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Informe um programa de milhas: SMILES, LATAM PASS, TUDOAZUL")


@retry(NetworkError, tries=3)
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Hello, I am your bot!')


@retry(NetworkError, tries=3)
async def handle_message(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You said: {update.message.text}")
    # await update.message.reply_text('You said: ' + update.message.text)


@app.route('/' + TOKEN, methods=['POST'])
async def webhook() -> tuple[str, int]:
    if request.method == "POST":
        update = Update.de_json(await request.get_json(force=True), application.bot)
        logger.debug(f"Update {update}")
        await application.process_update(update)
        db.save_chat_if_not_exist({'chat_id': update.effective_chat.id})
    return "ok", 200


@app.route('/broadcast', methods=['POST'])
async def broadcast() -> tuple[str, int]:
    payload = await request.get_json(force=True)
    logger.debug(f"Broadcasting the message {payload}")
    chats = db.get_values()
    for chat in chats:
        await application.bot.send_message(chat_id=chat['chat_id'], text=payload['message'])
    return "ok", 200


@app.route('/health')
async def hello():
    return 'The application is healthy!'


async def run_telegram_bot():
    # Use this function to start the bot
    await application.initialize()
    await application.bot.setWebhook(url=WEBHOOK + TOKEN)
    await application.start()


@app.before_serving
async def before_serving():
    db.start()
    # Run the Telegram bot in a background task using Quart's event loop
    await asyncio.create_task(run_telegram_bot())


@app.after_serving
async def after_serving():
    await application.stop()
    await application.shutdown()


application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


def main():
    # Start Flask application
    app.run(port=5000)


if __name__ == '__main__':
    main()
