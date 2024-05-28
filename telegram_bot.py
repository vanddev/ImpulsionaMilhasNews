import logging
import os

import firebase as db
from retry import retry
from telegram import Update
from telegram.error import NetworkError
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

import api_client

TOKEN = os.getenv('BOT_TOKEN', '')
WEBHOOK = os.getenv('WEBHOOK_URL', '')

__application = (Application.builder().token(TOKEN).read_timeout(10)
                 .write_timeout(10).connect_timeout(10).pool_timeout(10).build())

logger = logging.getLogger()


def __update_command_track(context: CallbackContext, command: str):
    context.user_data["LAST_COMMAND"] = command


def __clean_command_track(context: CallbackContext):
    context.user_data["LAST_COMMAND"] = None


def __get_last_command(context: CallbackContext):
    return context.user_data.get("LAST_COMMAND")


@retry(NetworkError, tries=3)
async def check_context(update: Update, context: CallbackContext):
    if not context.args:
        message = update.message.text.lower()
        command = message.replace("/", "")
        __update_command_track(context, command)
        await update.message.reply_text(text="Informe um programa de milhas: SMILES, LATAMPASS, TUDOAZUL")
    else:
        message = update.message.text.lower()
        command = message.split(" ")[0].replace("/", "")
        await globals()[command](update, context)


@retry(NetworkError, tries=3)
async def ofertas(update: Update, context: CallbackContext, airline=None):
    __clean_command_track(context)
    has_args = False
    if not airline:
        has_args = True
        airline = context.args[0].lower()
    await update.message.reply_text(text=f"Procurando promoções da {airline}")
    offers = api_client.get_offers_by_ffp(airline)
    if not offers:
        await update.message.reply_text(text="Nenhuma oferta disponivel")
    for offer in offers:
        await update.message.reply_text(parse_mode='HTML',
                                        text=format_offer_message(offer))
    if not has_args:
        await update.message.reply_text(text=f"Você também pode pesquisar informando diretamente a companhia aerea no "
                                             f"comando, ex: /ofertas {airline}")


@retry(NetworkError, tries=3)
async def handle_message(update: Update, context: CallbackContext) -> None:
    command_running = __get_last_command(context)
    if command_running:
        await globals()[command_running](update, context, update.message.text.lower())


@retry(NetworkError, tries=3)
async def inscricao(update: Update, context: CallbackContext, args) -> None:
    __clean_command_track(context)
    has_args = False
    if not args:
        has_args = True
        args = context.args[0].lower()
    chat = db.get_chat_by_id(update.effective_chat.id)
    subscribed_to = chat[1]['subscribed_to'] if 'subscribed_to' in chat[1] else []
    if args not in subscribed_to:
        subscribed_to.append(args)
        db.update(chat[0], {'subscribed_to': subscribed_to})
    await update.message.reply_text(
        f"Agora você está inscrito para receber ofertas de milhas aereas da {args}")

    if not has_args:
        await update.message.reply_text(text=f"Você também pode fazer a inscrição informando diretamente a companhia "
                                             f"aerea no comando, ex: /inscricao {args}")


@retry(NetworkError, tries=3)
async def minhasinscricoes(update: Update, context: CallbackContext):
    chat = db.get_chat_by_id(update.effective_chat.id)
    subscribed_to = chat[1]['subscribed_to'] if 'subscribed_to' in chat[1] else []
    await update.message.reply_text(
        f"Você está inscrito para receber ofertas das seguintes companhias aereas: {', '.join(subscribed_to)}")


@retry(NetworkError, tries=3)
async def removerinscricao(update: Update, context: CallbackContext, args) -> None:
    __clean_command_track(context)
    has_args = False
    if not args:
        has_args = True
        args = context.args[0].lower()
    chat = db.get_chat_by_id(update.effective_chat.id)
    subscribed_to = chat[1]['subscribed_to'] if 'subscribed_to' in chat[1] else []
    if args in subscribed_to:
        subscribed_to.remove(args)
        db.update(chat[0], {'subscribed_to': subscribed_to})
    await update.message.reply_text(
        f"Sua inscrição foi encerrada e você não receberá mais ofertas da {args}")

    if not has_args:
        await update.message.reply_text(text=f"Você também pode remover a inscrição informando diretamente a companhia "
                                             f"aerea no comando, ex: /removerinscricao {args}")


async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error.message}")


@retry(NetworkError, tries=3)
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Oi! Aqui você pode acompanhar as ofertas de transferencia de milha, aproveite para viajar bastante.')


async def send_message(chat_id, text):
    await __application.bot.send_message(chat_id, text, parse_mode='HTML')


async def process_update_json(json):
    update = Update.de_json(json, __application.bot)
    # logger.debug(f"Update {update}")
    await __application.process_update(update)
    return update


def format_offer_message(offer):
    return f"<b>{offer['title']}</b>\r\n\r\nOferta disponivel até <b>{offer['deadline']}</b>\r\n\r\n{offer['original_url']}"


async def start_bot():
    await __application.initialize()
    await __application.bot.setWebhook(url=WEBHOOK + TOKEN)
    await __application.start()


async def stop_bot():
    await __application.stop()
    await __application.shutdown()


__application.add_handler(CommandHandler('start', start))
__application.add_handler(CommandHandler('ofertas', check_context))
__application.add_handler(CommandHandler('inscricao', check_context))
__application.add_handler(CommandHandler('minhasinscricoes', minhasinscricoes))
__application.add_handler(CommandHandler('removerinscricao', check_context))
__application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
__application.add_error_handler(error_handler)
