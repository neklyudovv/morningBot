import telebot
import time as timelib
import datetime
import requests
from threading import Thread
from lxml import html

TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)
USERS = {}
TIME = {}

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

def inform(chat_id, time):
	weather = get_weather(USERS[chat_id])
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
		for user in USERS:
			if now == TIME[user]:
				inform(user, TIME[user])
		timelib.sleep(60)

thread = Thread(target=check_time, args=([USERS])) # создаем поток

@bot.message_handler(commands=['start'])
def start(message):
	if message.chat.id not in USERS: # если пользователь не активировал бота
		USERS[message.chat.id] = 'Москва'
		TIME[message.chat.id] = '6:30'
		second_part = '\nКаждый день в ' + TIME[message.chat.id] + ' я буду сообщать тебе о последних новостях, погоде на улице и другую полезную информацию\n\nКоманды бота:\n/city {город} - изменить город\n/time {время формата 6:30} - изменить время'
		bot.send_message(message.chat.id, ("Привет, {0.first_name}!").format(message.from_user, bot.get_me())+second_part, parse_mode='html')
		print('Бот активирован пользователем {0.first_name}'.format(message.from_user, bot.get_me())) # хоть какое-то подобие логирования в консоль
		if not thread.is_alive():
			thread.start()
	else:
		bot.send_message(message.chat.id, (("Да активировал ты уже его, успокойся").format(message.from_user, bot.get_me())))

@bot.message_handler(commands=['city'])
def slashcity(message):
	global USERS
	if message.text == '/city':
		bot.send_message(message.chat.id, 'Текущий город - ' + USERS[message.chat.id] + '\nИзменить город: /city {город}', parse_mode='html')
	else:
		local_city = message.text.replace('/city', '').replace(' ', '')
		USERS[message.chat.id] = local_city
		bot.send_message(message.chat.id, f'Вы успешно изменили город на {local_city}', parse_mode='html')
		print(('{0.first_name} изменил(a) город на ' + local_city).format(message.from_user, bot.get_me()))

@bot.message_handler(commands=['time'])
def slashtime(message):
	global TIME
	if message.text == '/time':
		bot.send_message(message.chat.id, 'Время отправки сообщения: ' + TIME[message.chat.id] + '\nИзменить время: /time {время формата 6:30}', parse_mode='html')
	else:
		new_time = message.text.replace('/time', '').replace(' ', '')
		TIME[message.chat.id] = new_time
		bot.send_message(message.chat.id, f'Вы успешно изменили время на {new_time}', parse_mode='html')
		print(('{0.first_name} изменил(a) время на ' + new_time).format(message.from_user, bot.get_me()))

if __name__ == '__main__':
	bot.polling(none_stop=True) 