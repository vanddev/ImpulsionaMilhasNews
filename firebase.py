import logging
import os
from typing import List, Any

import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import db

CREDENTIAL_LOCATION = os.getenv('FIREBASE_CREDENTIAL_LOCATION', '')
DATABASE_URL = os.getenv('FIREBASE_DB_URL', '')

logger = logging.getLogger('quart.app')


def start():
    logger.debug("Fetching Firebase credential")
    resp = requests.get(CREDENTIAL_LOCATION)
    logger.debug("Firebase credential retrieved")
    cred = credentials.Certificate(resp.json())
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
    logger.info("Firebase initialized")


def get_data() -> dict:
    return __get_ref().get()


def get_values() -> list[Any]:
    return list(get_data().values()) if get_data() else []


def save(data: dict):
    logger.debug(f"Saving data on firebase db: {data}")
    __get_ref().push().set(data)
    logger.debug(f"Data saved: {data}")

def update(key, data: dict):
    __get_ref().child(key).update(data)


def delete(key):
    __get_ref().child(key).set({})


def save_chat_if_not_exist(chat):
    chats = get_values()
    chat_saved = list(filter(lambda item: ('chat_id' in item and item['chat_id'] == chat['chat_id']), chats))
    if not chat_saved:
        save(chat)


def __get_ref():
    return db.reference('/chats')


if __name__ == '__main__':
    start()
    print(get_data())
