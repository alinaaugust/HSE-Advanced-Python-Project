from werkzeug.security import generate_password_hash, check_password_hash


class Data:
    def __init__(self, db):
        self.__cursor = db.cursor()
        self.__db = db

    def add_user(self, log, psw):
        self.__cursor.execute(f"SELECT COUNT() as 'count' FROM logins WHERE login LIKE '{log}'")
        res = self.__cursor.fetchone()
        if res['count'] > 0:
            return False
        self.__cursor.execute("INSERT INTO logins VALUES(NULL, ?, ?, ?, ?)", (log, generate_password_hash(psw), "", ""))
        self.__db.commit()
        return True

    def check_login(self, log, psw):
        self.__cursor.execute(f"SELECT user_id, password FROM logins WHERE login LIKE '{log}'")
        res = self.__cursor.fetchone()
        if res and check_password_hash(res['password'], psw):
            return res['user_id']
        return 0

    def get_rows(self):
        self.__cursor.execute(f"SELECT title_id, title, average_rating FROM movie")
        res = self.__cursor.fetchall()
        return res

    def get_film(self, id):
        self.__cursor.execute(f"SELECT title_id, title, release_date, average_rating, genres FROM movie WHERE title_id LIKE '{id}'")
        res = self.__cursor.fetchall()
        return res

    def get_film_add_info(self, id):
        self.__cursor.execute(f"SELECT director, actors, description, duration FROM movie_add_info WHERE title_id LIKE '{id}'")
        res = self.__cursor.fetchall()
        return res

    def get_watched(self, user_id):
        self.__cursor.execute(f"SELECT watched FROM logins WHERE user_id LIKE '{user_id}'")
        res = self.__cursor.fetchone()
        return res[0]

    def set_watched(self, user_id, watch):
        self.__cursor.execute(f"UPDATE logins SET watched = '{watch}' WHERE user_id LIKE '{user_id}'")
        self.__db.commit()

    def check_if_watched(self, user_id, film_id):
        plan = self.get_watched(user_id)
        lis = plan.split('\n')
        titles = []
        for string in lis:
            if string:
                titles.append(string.split(' ')[0])
        return film_id not in titles

    def get_planned(self, user_id):
        self.__cursor.execute(f"SELECT planned FROM logins WHERE user_id LIKE '{user_id}'")
        res = self.__cursor.fetchone()
        return res[0]

    def set_planned(self, user_id, plann):
        print(plann)
        self.__cursor.execute(f"UPDATE logins SET planned = '{plann}' WHERE user_id LIKE '{user_id}'")
        self.__db.commit()

    def check_if_planned(self, user_id, film_id):
        plan = self.get_planned(user_id)
        lis = plan.split('\n')
        return film_id not in lis

    def get_title(self, li):
        titles = []
        for i in range(len(li)):
            if li[i]:
                self.__cursor.execute(f"SELECT title FROM movie WHERE title_id='{li[i]}'")
                res = self.__cursor.fetchone()
                titles.append((res['title'], li[i]))
        return titles

    def get_title_watched(self, lis):
        li = []
        titles = []
        for string in lis:
            if string:
                li.append(string.split(' ')[0])
        for id in li:
            if id:
                self.__cursor.execute(f"SELECT title FROM movie WHERE title_id='{id}'")
                res = self.__cursor.fetchone()
                titles.append(res['title'])
        return titles

    def get_rating_watched(self, li):
        rating = []
        for string in li:
            if string:
                rating.append(string.split(' ')[1])
        return rating

    def get_rating(self, user_id, film_id):
        watched = self.get_watched(user_id).split('\n')
        for movie in watched:
            if movie.startswith(film_id):
                a = movie.split(' ')
                return a[1]

    def delete_planned(self, planned, film_id):
        plan = planned.replace(film_id+'\n', '')
        return plan

