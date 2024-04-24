import asyncio
import logging
import threading

from quart import Quart, request

import async_thread
import firebase as db
import telegram_bot

app = Quart(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger('quart.app')
telegram_bot.logger = logger


@app.route('/' + telegram_bot.TOKEN, methods=['POST'])
async def webhook() -> tuple[str, int]:
    if request.method == "POST":
        update = await telegram_bot.process_update_json(await request.get_json(force=True))
        db.save_chat_if_not_exist({'chat_id': update.effective_chat.id})
    return "ok", 200


@app.route('/broadcast', methods=['POST'])
async def broadcast() -> tuple[str, int]:
    payload = await request.get_json(force=True)
    logger.debug(f"Broadcasting the message {payload}")
    chats = db.get_values()
    for chat in chats:
        async_thread.submit_async(telegram_bot.send_message(chat_id=chat['chat_id'], text=payload['message']))
    return "ok", 200


def required_field_validation(field, payload):
    if field not in payload:
        return f"field {field} is required"


@app.route('/broadcast/subscribed', methods=['POST'])
async def subscribed_broadcast():
    payload = await request.get_json(force=True)
    group = request.args.get('group')
    # errors_validation = [required_field_validation('message', payload),
    #                      required_field_validation('airline_group', payload)]
    # if errors_validation and not (all(error is None for error in errors_validation)):
    #     return errors_validation, 400
    logger.info(f"Broadcasting the message {payload}")
    chats_subscribed = db.get_chats_by_subscription(group)
    for chat in chats_subscribed:
        send_offers(chat["chat_id"], payload)
    return "ok", 200


def send_offers(chat_id, offers):
    for offer in offers:
        async_thread.submit_async(telegram_bot.send_message(chat_id=chat_id,
                                                            text=telegram_bot.format_offer_message(offer)))


@app.route('/health')
async def hello():
    return 'The application is healthy!'


@app.before_serving
async def before_serving():
    db.start()
    # Run the Telegram bot in a background task using Quart's event loop
    await asyncio.create_task(telegram_bot.start_bot())


@app.after_serving
async def after_serving():
    await telegram_bot.stop_bot()


def main():
    # Start Flask application
    app.run(port=5000)


if __name__ == '__main__':
    main()
