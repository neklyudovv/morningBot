import telebot
import time as timelib
import datetime
import requests
from threading import Thread
from lxml import html

TOKEN = 'token' # токен Телеграм бота 
bot = telebot.TeleBot(TOKEN)
USERS = {}
TIME = {}

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
	url = f'http://wttr.in/{city}?http://wttr.in/kazan?0&format=j1&lang=ru&m&M'
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
	news = body.xpath('//a[@class="home-link list__item-content list__item-content_with-icon home-link_black_yes"]')
	result = ''
	for i in range(0, 5):
		result += f'📌 <a href="{news[i].attrib["href"]}">{news[i].text_content()}</a> \n'
	return f'📰 Пока ты спал:\n{result}'

# Отправка уже готового сообщения
def inform(chat_id, time):
	weather = get_weather(USERS[chat_id])
	currency = get_currency()
	news = get_news()
	now = int(time[0:2].replace(':', ''))
	if now >= 4 and now <= 12:
		first_part = 'Доброе утро!'
	elif now >= 12 and now <= 18:
		first_part = 'Добрый день!'
	elif now >= 18 and now <= 23:
		first_part = 'Добрый вечер!'
	else:
		first_part = 'Доброй ночи!'
	bot.send_message(chat_id, f"{first_part} Время - {time}.\n\n{weather}\n\n{currency}\n\n{news}", parse_mode='html')
	print('Сообщение отправлено!')

# Ну чтобы не пропустить оптравку нужно и время проверять
def check_time(USERS):
	while True:
		hours = int(datetime.datetime.utcnow().strftime('%H')) + 3
		now = datetime.datetime.utcnow().strftime(f'{hours}:%M')
		if len(now) == 5:
		    if int(now[0:2]) >= 24:
			    now == str(int(now[0:2]) - 21) + now[2:5]
		for user in USERS:
			if now == TIME[user]:
				inform(user,TIME[user])
		timelib.sleep(60)

thread = Thread(target=check_time, args=([USERS])) # создаем поток

# Обработка запуска бота
@bot.message_handler(commands=['start'])
def start(message):
	if message.chat.id not in USERS: # если пользователь не активировал бота
		USERS[message.chat.id] = 'Москва'
		TIME[message.chat.id] = '6:30'
		second_part = '\nКаждый день в ' + TIME[message.chat.id] + ' я буду сообщать тебе о последних новостях, погоде на улице и другую полезную информацию\n\nКоманды бота:\n/city {город} - изменить город\n/time {время формата 6:30} - изменить время'
		bot.send_message(message.chat.id, ("Привет, {0.first_name}!").format(message.from_user, bot.get_me())+second_part, parse_mode='html')
		print('Бот активирован пользователем {0.first_name}'.format(message.from_user, bot.get_me()))
		if not thread.is_alive():
			thread.start()
	else:
		bot.send_message(message.chat.id, (("Да активировал ты уже его, успокойся").format(message.from_user, bot.get_me())))

# Обработка изменения города 
@bot.message_handler(commands=['city'])
def slashcity(message):
	global USERS
	if message.text == '/city':
		bot.send_message(message.chat.id, 'Текущий город - ' + USERS[message.chat.id] + '\nИзменить город: /city {город}', parse_mode='html')
	else:
		local_city = message.text.replace('/city', '').replace(' ', '')
		request_headers = {
    	'Accept-Language' : 'ru'
		}
		response = requests.get(f'http://wttr.in/{local_city}', headers=request_headers)
		if response.text.count('определить не удалось') == 0:
			USERS[message.chat.id] = local_city
			bot.send_message(message.chat.id, f'Вы успешно изменили город на {local_city}', parse_mode='html')
			print(('{0.first_name} изменил(a) город на ' + local_city).format(message.from_user, bot.get_me()))
		else:
			bot.send_message(message.chat.id, f'Некорректный город', parse_mode='html')

# Обработка изменения времени отправки сообщения
@bot.message_handler(commands=['time'])
def slashtime(message):
	global TIME
	if message.text == '/time':
		bot.send_message(message.chat.id, 'Время отправки сообщения: ' + TIME[message.chat.id] + '\nИзменить время: /time {время формата 6:30}', parse_mode='html')
	else:
		new_time = message.text.replace('/time', '').replace(' ', '')
		if len(new_time) == 5:
			if new_time[2] == ':':
				TIME[message.chat.id] = new_time
				bot.send_message(message.chat.id, f'Вы успешно изменили время на {new_time}', parse_mode='html')
			else:
				bot.send_message(message.chat.id, f'Некорректное время', parse_mode='html')
		else:
			if new_time[1] == ':':
				TIME[message.chat.id] = new_time
				bot.send_message(message.chat.id, f'Вы успешно изменили время на {new_time}', parse_mode='html')
			else:
				bot.send_message(message.chat.id, f'Некорректное время', parse_mode='html')
		print(('{0.first_name} изменил(a) время на ' + new_time).format(message.from_user, bot.get_me()))

if __name__ == '__main__':
	bot.polling(none_stop=True)