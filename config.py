import sqlite3

from db import Bot
Bot = Bot('bot.db')

USERS = Bot.get_users()
TOKEN = ''