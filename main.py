import telebot
import time as timelib
import datetime
import requests
from threading import Thread

TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)
USERS = []
time = '6:30'
city = 'Москва'

def get_weather(city):
	response = requests.get(f'http://ru.wttr.in/{city}?0T')
	state = response.text[40:50].replace(' ','').replace('\n', '') # достаем из строки погоду и убираем пробелы с ентерами
	degrees = response.text[62:75].replace(' ','').replace('\n', '') # то же самое но с температурой
	return f'Погода в г. {city} - {state}, {degrees}'

def inform(chat_id):
	weather = get_weather(city)
	if time >= '4:00' and time <= "12:00":
		first_part = 'Доброе утро!'
	elif time >= "12:00" and time <= "18:00":
		first_part = 'Добрый день!'
	elif time >= "18:00" and time <= "23:00":
		first_part = 'Добрый вечер!'
	else:
		first_part = 'Доброй ночи!'
	bot.send_message(chat_id, f"{first_part} Время - {time}.\n{weather}", parse_mode='html')
	print('Сообщение отправлено!')

def check_time(USERS):
	while True:
		hours = int(datetime.datetime.utcnow().strftime('%H')) + 3
		now = datetime.datetime.utcnow().strftime(f'{hours}:%M')
		if now == time:
			for user in USERS:
				inform(user)
		timelib.sleep(60)

thread = Thread(target=check_time, args=([USERS])) # создаем поток

@bot.message_handler(commands=['start'])
def start(message):
	if message.chat.id not in USERS: # если пользователь не активировал бота
		USERS.append(message.chat.id)
		second_part = f'\nКаждый день в {time} я буду сообщать тебе о последних новостях, погоде на улице и другую полезную информацию'
		bot.send_message(message.chat.id, ("Привет, {0.first_name}!" + second_part).format(message.from_user, bot.get_me()), parse_mode='html')
		#print('Бот активирован пользователем {0.first_name}'.format(message.from_user, bot.get_me())) # хоть какое-то подобие логирования в консоль
		if not thread.is_alive():
			thread.start()
	else:
		bot.send_message(message.chat.id, (("Да активировал ты уже его, успокойся").format(message.from_user, bot.get_me())))

if __name__ == '__main__':
	bot.polling(none_stop=True) 