import time
import json
import requests
import urllib
import webscrap
from os import environ
import textwrap
try:
    import configparser
    from configparser import NoSectionError
except ImportError:
    import ConfigParser as configparser
    from ConfigParser import NoSectionError

from datetime import datetime
from threading import Timer

try:
    CONFIG = configparser.ConfigParser()
    CONFIG.read("sample.ini")
    TOKEN = CONFIG.get('CREDS', 'API_TOKEN')
except NoSectionError:
    TOKEN = environ['TOKEN']

URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
            url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=markdown".format(text, chat_id)
    get_url(url)

def handle_updates(updates):
    for update in updates["result"]:
        if "channel_post" in update:
            text = update["channel_post"]["text"]
            chat = update["channel_post"]["chat"]["id"]
        else:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
        if text == "/start":
            intro_message = textwrap.dedent("""
            Welcome to Train Bot!
            This bot will show you the current status of Saurashtra Express and Firozpur Express.
            To get the current status of Saurashtra Express enter /Saurashtra.
            To get the current status of the Firozpur Express, enter /Firozpur.
            Join the [Channel](https://t.me/train_status) to get a notification everyday at 3:00pm for the live status of Saurashtra Express.
            """)
            send_message(intro_message, chat)
        elif text == "/Saurashtra":
            try:
                text1 = webscrap.train_delay('19016', 'PLG')
                chat = update["message"]["chat"]["id"]
                send_action(chat, "typing")
                send_message(text1, chat)
            except Exception as e:
                print(e)
        elif text == "/Firozpur":
            try:
                text1 = webscrap.train_delay('19024', 'PLG')
                chat = update["message"]["chat"]["id"]
                send_action(chat,"typing")
                send_message(text1, chat)
            except Exception as e:
                print(e)

        
def channel_send():
    chatid="@train_status"
    text2=webscrap.train_delay('19016', 'PLG')
    text = urllib.parse.quote_plus(text2)
    url = URL + "sendMessage?chat_id={}&text={}".format(chatid, text)
    get_url(url)

def send_action(chatid, action):
    url = URL + "sendChatAction?chat_id={}&action={}".format(chatid, action)
    requests.get(url)

x=datetime.today()
y=x.replace(day=x.day, hour=15, minute=0, second=0, microsecond=0)
delta_t=y-x

secs=delta_t.seconds+1

t = Timer(secs, channel_send)
t.start()

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()

