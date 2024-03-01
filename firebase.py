import json
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

FIREBASE_SDK_TOKEN = os.getenv('FIREBASE_SDK_TOKEN', '')
DATABASE_URL = os.getenv('FIREBASE_DB_URL', '')
TOKEN_JSON = 'token.json'


def start():
    with open(TOKEN_JSON, 'w') as f:
        f.write(FIREBASE_SDK_TOKEN)
    cred = credentials.Certificate(TOKEN_JSON)
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})


def get_data() -> dict:
    return __get_ref().get()


def save(data: dict):
    __get_ref().push().set(data)


def update(key, data: dict):
    __get_ref().child(key).update(data)


def delete(key):
    __get_ref().child(key).set({})


def filter_chat(chat):
    if chat.id == '':
        return True
    else:
        return False


def save_chat_if_not_exist(chat):
    chats = list(get_data().values()) if get_data() else []
    chat_saved = list(filter(lambda item: ('chat_id' in item and item['chat_id'] == chat['chat_id']), chats))
    if not chat_saved:
        save(chat)


def __get_ref():
    return db.reference('/chats')


if __name__ == '__main__':
    start()
    print(save_chat_if_not_exist({"chat_id": 'abcqwert'}))
