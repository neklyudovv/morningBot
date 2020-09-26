import telebot
import time as timelib
import datetime
import requests
from threading import Thread

TOKEN = 'your token'
time = '6:30'
city = 'Москва'
bot = telebot.TeleBot(TOKEN)

def get_weather(chat_id, city):
	response = requests.get(f'http://ru.wttr.in/{city}?0T')
	state = response.text[40:50].replace(' ','').replace('\n', '') # достаем из строки погоду и убираем пробелы с ентерами
	degrees = response.text[62:75].replace(' ','').replace('\n', '') # то же самое но с температурой
	return f'Погода в г. {city} - {state}, {degrees}'

def inform(chat_id):
	weather = get_weather(chat_id, city)
	bot.send_message(chat_id, f"Доброе утро! Время - {time}.\n{weather}", parse_mode='html')
	print('Сообщение отправлено!')

def check_time(chat_id):
	while True:
		hours = int(datetime.datetime.utcnow().strftime('%H')) + 3
		now = datetime.datetime.utcnow().strftime(f'{hours}:%M')
		if now == time:
			inform(chat_id)
		timelib.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
	second_part = f'\nКаждый день в {time} я буду сообщать тебе о последних новостях, погоде на улице и другую полезную информацию'
	bot.send_message(message.chat.id, ("Привет, {0.first_name}!" + second_part).format(message.from_user, bot.get_me()), parse_mode='html')
	thread = Thread(target=check_time, args=([message.chat.id]))
	thread.start()
	print('Бот активирован пользователем {0.first_name}')

if __name__ == '__main__':
	bot.polling(none_stop=True)