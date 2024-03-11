import os

import requests

API_URL = os.getenv('NEWS_API_URL')


def get_offers_by_ffp(ffp):
    response = requests.get(f"{API_URL}?group={ffp}")
    return response.json()
