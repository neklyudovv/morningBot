import sqlite3

class Bot:
	# Для более легкого добавления возможных новых запросов к бд, вынес их в класс

	def __init__(self, db_file):
		self.con = sqlite3.connect(db_file, check_same_thread = False)
		self.cursor = self.con.cursor()

	def get_users(self):
		r = self.con.execute('SELECT * FROM `users`')

		cur = self.con.cursor() 
		try:
			cur.execute('SELECT * FROM `users`') 
			r = cur.fetchall()
			cur.close()
			return r
		except:
			return 'Ошибка бд'

	def add_user(self, user_id, user_city, user_time):
		r = self.con.execute('INSERT INTO `users` (`id`, `city`, `time`) VALUES (?,?,?)', (int(user_id), str(user_city), str(user_time),))
		return self.con.commit()

	def edit_user_city(self, user_id, user_city):
		r = self.con.execute('UPDATE `users` SET `city` = (?) WHERE `id` = (?)', (str(user_city), int(user_id),))
		return self.con.commit()

	def edit_user_time(self, user_id, user_time):
		r = self.con.execute('UPDATE `users` SET `time` = (?) WHERE `id` = (?)', (str(user_time), int(user_id),))
		return self.con.commit()

	def close_con(self):
		self.con.close()