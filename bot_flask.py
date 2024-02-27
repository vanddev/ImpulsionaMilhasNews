import asyncio

from quart import Quart, request
from retry import retry
import logging

from telegram import Update
from telegram.error import NetworkError
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

app = Quart(__name__)

TOKEN = "6907228198:AAEBGml4pXqomfjRYBNnAcLkPxA6OluuPq4"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
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


@retry(NetworkError, tries=3)
async def start_application(appli):
    await appli.bot.setWebhook(url='https://goat-genuine-logically.ngrok-free.app/' + TOKEN)


@app.route('/' + TOKEN, methods=['POST'])
async def webhook() -> str:
    if request.method == "POST":
        update = Update.de_json(await request.get_json(force=True), application.bot)
        application.update_queue.put(update)
        # start(update)
        # asyncio.run(application.process_update(update))
    return "ok"


@app.route('/hello')
async def hello():
    return 'Hello, World!'


def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling())
    loop.close()


application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    from threading import Thread
    t = Thread(target=run_asyncio_loop)
    t.start()
    # Start Flask application
    app.run(port=5000)