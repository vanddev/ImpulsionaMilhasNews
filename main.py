import logging
import os
from enum import Enum

from retry import retry
from telegram import Update
from telegram.error import NetworkError
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = "6907228198:AAEBGml4pXqomfjRYBNnAcLkPxA6OluuPq4"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)


class COMMANDS(Enum):
    ULTIMA_PROMOCAO = 1


@retry(NetworkError, tries=3)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Oi Elziana!")


@retry(NetworkError, tries=3)
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Compre Milhas Smiles com até 300% de Bônus e Aproveite as Vantagens\r\n\r\nSe você é cliente Smiles, esta é a oportunidade perfeita para adquirir milhas e receber um bônus incrível! A promoção oferece até 300% de bônus na compra de milhas, válida até às 21 horas do dia 20 de fevereiro de 2024.\r\n\r\nOs benefícios variam de acordo com o seu status no programa Smiles:\r\n\r\nCliente Smiles: recebe 150% de bônus na compra de milhas.\r\n\r\nCliente Clube Smiles 1000: recebe 200% de bônus.\r\n\r\nCliente Clube Smiles 2000: recebe 220% de bônus.\r\n\r\nCliente Clube Smiles 5000: recebe 240% de bônus.\r\n\r\nCliente Clube Smiles 7000: recebe 260% de bônus.\r\n\r\nCliente Clube Smiles 10000: recebe 280% de bônus.\r\n\r\nCliente Clube Smiles 20000 ou Diamante: recebe o máximo de 300% de bônus.\r\n\r\nSe você ainda não faz parte do Clube Smiles, esta é uma excelente oportunidade para se associar e desfrutar de benefícios exclusivos, como bônus extra na compra de milhas. Quanto maior o seu plano no Clube Smiles, maior será o seu bônus, chegando a até 300% de bônus para os membros do Clube Smiles 20000 ou Diamante.\r\n\r\nAs milhas adquiridas podem ser utilizadas para resgates de passagens aéreas, upgrades de categoria, diárias de hotéis, aluguel de carros e muito mais. Aproveite essa oferta exclusiva e planeje sua próxima viagem com a Smiles!\r\n\r\nPara participar da promoção, basta acessar o site da Smiles, realizar a compra de milhas e aproveitar os bônus especiais. Lembre-se de que a oferta é válida por tempo limitado, então não perca essa oportunidade de turbinar o seu saldo de milhas e viajar com ainda mais vantagens!")
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


@retry(NetworkError, tries=3)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await get_last_command(context) == COMMANDS.ULTIMA_PROMOCAO:
        await ultima_promocao(update, context, update.message.text)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


@retry(NetworkError, tries=3)
async def prev_ultima_promocao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update_command_track(context, COMMANDS.ULTIMA_PROMOCAO)
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Informe um programa de milhas: SMILES, LATAM PASS, TUDOAZUL")
    else:
        await ultima_promocao(update, context)


@retry(NetworkError, tries=3)
async def ultima_promocao(update: Update, context: ContextTypes.DEFAULT_TYPE, airline=None):
    has_args = False
    if not airline:
        has_args = True
        airline = context.args[0]
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Procurando promoções da {airline}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"2 promoções da {airline} encontradas")
    if not has_args:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Você também pode pesquisar informando diretamente a companhia aerea no "
                                            f"comando, ex: /ultima_promocao {airline}")


async def error_handler(update, context):
    # print(update)
    logging.error(f"Update {update} caused error {context.error.message}")


async def update_command_track(context: ContextTypes.DEFAULT_TYPE, command: COMMANDS):
    context.user_data["LAST_COMMAND"] = command


async def get_last_command(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("LAST_COMMAND")


if __name__ == '__main__':
    application = (
        ApplicationBuilder().token(TOKEN).read_timeout(10).write_timeout(10).connect_timeout(10).pool_timeout(
            10).build())

    application.add_handler(CommandHandler('ultima_promocao', prev_ultima_promocao))
    application.add_handler(CommandHandler('caps', caps))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_error_handler(error_handler)
    # application.run_polling()
    application.run_webhook(listen="0.0.0.0",
                            port=int(os.environ.get('PORT', 5000)),
                            url_path=TOKEN,
                            webhook_url=os.getenv("WEBHOOK_URL")+TOKEN)
