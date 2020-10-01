import telebot
import time as timelib
import datetime
import requests
from threading import Thread
from lxml import html

TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)
USERS = []
time = '23:22'
city = 'Москва'

def get_currency():
	response = requests.get('https://yandex.ru')
	body = html.fromstring(response.text)
	dollar = body.xpath('//span[@class="inline-stocks__value_inner"]/text()')[0]
	euro = body.xpath('//span[@class="inline-stocks__value_inner"]/text()')[1]
	return f'Курсы валют: 1 EUR = {euro} RUB; 1 USD = {dollar} RUB.'

def get_weather(city):
	url = f'http://wttr.in/{city}?0T'
	request_headers = {
    	'Accept-Language' : 'ru'
	}
	response = requests.get(url, headers=request_headers)
	state = response.text[40:50].replace(' ','').replace('\n', '') # достаем из строки погоду и убираем пробелы с ентерами
	degrees = response.text[58:75].replace(' ','').replace('\n', '') # то же самое но с температурой
	return f'Погода в г. {city} - {state}, {degrees}'

def inform(chat_id):
	weather = get_weather(city)
	currency = get_currency()
	if time >= '4:00' and time <= "12:00":
		first_part = 'Доброе утро!'
	elif time >= "12:00" and time <= "18:00":
		first_part = 'Добрый день!'
	elif time >= "18:00" and time <= "23:00":
		first_part = 'Добрый вечер!'
	else:
		first_part = 'Доброй ночи!'
	bot.send_message(chat_id, f"{first_part} Время - {time}.\n{weather}\n{currency}", parse_mode='html')
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
		print('Бот активирован пользователем {0.first_name}'.format(message.from_user, bot.get_me())) # хоть какое-то подобие логирования в консоль
		if not thread.is_alive():
			thread.start()
	else:
		bot.send_message(message.chat.id, (("Да активировал ты уже его, успокойся").format(message.from_user, bot.get_me())))

@bot.message_handler(commands=['city'])
def slashcity(message):
	global city
	if message.text == '/city':
		bot.send_message(message.chat.id, f'Текущий город - {city}', parse_mode='html')
	else:
		local_city = message.text.replace('/city', '').replace(' ', '')
		city = local_city
		bot.send_message(message.chat.id, f'Вы успешно изменили город на {local_city}', parse_mode='html')

if __name__ == '__main__':
	bot.polling(none_stop=True) 