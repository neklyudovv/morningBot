import telebot
import time as timelib
import datetime
import requests
from threading import Thread
from lxml import html
from db import Bot as BotDB
import config


USERS = config.USERS
TOKEN = config.TOKEN

BotDB = BotDB('bot.db')

bot = telebot.TeleBot(TOKEN)


# Курс биткоина
def get_bitcoin_price():
	response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
	data = response.json()
	return (data["bpi"]["USD"]["rate"]).replace(',', '')[0:5]

# Курсы евро, доллара и их обьединение в одну строку
def get_currency():
	response = requests.get('https://yandex.ru')
	body = html.fromstring(response.text)
	dollar = body.xpath('//span[@class="inline-stocks__value_inner"]/text()')[0]
	euro = body.xpath('//span[@class="inline-stocks__value_inner"]/text()')[1]
	btc = get_bitcoin_price()
	return f'💵 Курсы валют:\n\n 💰1 EUR = {euro} RUB\n 💰1 USD = {dollar} RUB\n 💰1 btc = {btc} USD.'

# Получение данных о погоде
def get_weather(city):
	url = f'http://wttr.in/{city}?0&format=j1&lang=ru&m&M'
	request_headers = {
		'0' : '',
		'forman' : 'j1',
    	'lang' : 'ru',
    	'm' : '',
    	'M' : '',
	}
	response = requests.get(url, headers=request_headers)
	result = ((response.json())['current_condition'])[0]
	state = result['lang_ru'][0]['value']
	degrees = result['temp_C']
	return f'🌤 Погода в г. {city} - 🌡 {state},  {degrees} ℃'


# Получение пяти первых статей с Яндекса
def get_news():
	response = requests.get('https://yandex.ru')
	body = html.fromstring(response.text)
	news = body.xpath('//a[@class="home-link2 news__item list__item-content list__item-content_with-icon home-link2_color_inherit home-link2_hover_red"]')
	result = ''
	for i in range(0, 5):
		result += f'📌 <a href="{news[i].attrib["href"]}">{news[i].text_content()}</a> \n'
	return f'📰 Пока ты спал:\n{result}'

# Отправка уже готового сообщения
def inform(user):
	weather = get_weather(user[1])
	currency = get_currency()
	news = get_news()
	now = int(user[2][0:2].replace(':', ''))
	if now >= 4 and now < 12:
		first_part = 'Доброе утро!'
	elif now >= 12 and now < 18:
		first_part = 'Добрый день!'
	elif now >= 18 and now <= 23:
		first_part = 'Добрый вечер!'
	else:
		first_part = 'Доброй ночи!'
	bot.send_message(user[0], f"{first_part} Время - {user[2]}.\n\n{weather}\n\n{currency}\n\n{news}", parse_mode='html')
	#bot.send_message(chat_id, f"{first_part} Время - {time}.\n\n{weather}\n\n{currency}\n\n", parse_mode='html')
	print('Сообщение отправлено!')


def check_time(USERS):
	while True:
		USERS = BotDB.get_users()
		hours = int(datetime.datetime.utcnow().strftime('%H')) + 3
		now = datetime.datetime.utcnow().strftime(f'{hours}:%M')
		if len(now) == 5:
		    if int(now[0:2]) >= 24:
			    now = str(int(now[0:2]) - 21) + now[2:5]
		for user in USERS:
			if now == user[2]:
				inform(user)
		timelib.sleep(60)

thread = Thread(target=check_time, args=([USERS])) # создаем поток


if len(USERS) != 0:
    if not thread.is_alive():
        thread.start()


@bot.message_handler(commands=['start'])
def start(message):
	if message.chat.id not in [element for a_list in USERS for element in a_list]: # если пользователь не активировал бота
		BotDB.add_user(message.chat.id, 'Москва', '6:30')
		second_part = '\nКаждый день в 6:30 я буду сообщать тебе о последних новостях, погоде на улице и другую полезную информацию\n\nКоманды бота:\n/city {город} - изменить город\n/time {время формата 6:30} - изменить время'
		bot.send_message(message.chat.id, ("Привет, {0.first_name}!").format(message.from_user, bot.get_me())+second_part, parse_mode='html')
		print('Бот активирован пользователем {0.first_name}'.format(message.from_user, bot.get_me())) # хоть какое-то подобие логирования в консоль
		if not thread.is_alive():
			thread.start()
	else:
		bot.send_message(message.chat.id, (("Бот уже активирован").format(message.from_user, bot.get_me())))


@bot.message_handler(commands=['city'])
def slashcity(message):
	if message.text == '/city':
		current_city = ''
		for user in USERS:
			if user[0] == message.chat.id:
				current_city = user[1]

		bot.send_message(message.chat.id, 'Текущий город - ' + current_city + '\nИзменить город: /city {город}', parse_mode='html')
	else:
		local_city = message.text.replace('/city', '').replace(' ', '')
		request_headers = {
    	'Accept-Language' : 'ru'
		}
		response = requests.get(f'http://wttr.in/{local_city}', headers=request_headers)
		if response.text.count('определить не удалось') == 0:
			BotDB.edit_user_city(message.chat.id, local_city)
			bot.send_message(message.chat.id, f'Вы успешно изменили город на {local_city}', parse_mode='html')
			print(('{0.first_name} изменил(a) город на ' + local_city).format(message.from_user, bot.get_me()))
		else:
			bot.send_message(message.chat.id, f'Некорректный город', parse_mode='html')


@bot.message_handler(commands=['time'])
def slashtime(message):
	if message.text == '/time':
		current_time = ''
		for user in USERS:
			if user[0] == message.chat.id:
				current_time = user[2]
		bot.send_message(message.chat.id, 'Время отправки сообщения: ' + user[2] + '\nИзменить время: /time {время формата 6:30}', parse_mode='html')
	else:
		new_time = message.text.replace('/time', '').replace(' ', '')
		if len(new_time) == 5:
			if new_time[2] == ':':
				BotDB.edit_user_time(message.chat.id, new_time)
				bot.send_message(message.chat.id, f'Вы успешно изменили время на {new_time}', parse_mode='html')
			else:
				bot.send_message(message.chat.id, f'Некорректное время', parse_mode='html')
		else:
			if new_time[1] == ':':
				BotDB.edit_user_time(message.chat.id, new_time)
				bot.send_message(message.chat.id, f'Вы успешно изменили время на {new_time}', parse_mode='html')
			else:
				bot.send_message(message.chat.id, f'Некорректное время', parse_mode='html')
		print(('{0.first_name} изменил(a) время на ' + new_time).format(message.from_user, bot.get_me()))


if __name__ == '__main__':
	bot.polling(none_stop=True)