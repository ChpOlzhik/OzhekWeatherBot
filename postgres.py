import psycopg2
import config


class Db:
    def __init__(self):
        self.database = config.database
        self.user = config.user
        self.password = config.password
        self.host = config.host
        self.port = config.port
        self.conn = psycopg2.connect(database=self.database,
                                     user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)

    def connect(self):
        self.conn = psycopg2.connect(database=self.database,
                                     user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)

    def user_exists(self, user_id):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        cursor.execute('''select 1 from "Clients" where id = {0}'''.format(user_id))
        res = cursor.fetchall()
        self.conn.commit()
        if res:
            return True
        else:
            return False

    def add_user(self, user_id, username, surname):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        cursor.execute('''insert into "Clients" (id,name,surname) values({0}, '{1}', '{2}')'''.format(user_id, username, surname))
        self.conn.commit()

    def getLang(self, user_id):
        self.conn.autocommit = True
        cursor = self.conn.cursor()

        sql = '''select L.lang_key from "Languages" L inner join "Clients" C on C.lang_id = L.lang_id where C.id = {0}'''.format(user_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        return res[0][0]

    def getAllLang(self):
        self.conn.autocommit = True
        cursor = self.conn.cursor()

        sql = '''select name, lang_key from "Languages" order by(name)'''
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        return res

    def getLang(self, uid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()

        sql = '''select name, lang_key from "Languages" where lang_id in (select lang_id from "Clients" where id = {0})'''.format(uid)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        return res[0]

    def changeLang(self, lang_key, user_id):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''update "Clients" set lang_id = (select lang_id from "Languages" where lang_key = '{0}' limit 1) where id = {1} '''.format(lang_key, user_id)
        cursor.execute(sql)
        self.conn.commit()

    def findCity(self, cid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''select * from "Cities" where c_id = {0}'''.format(cid)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        if res:
            return True
        else:
            return False

    def insertCity(self, cid, c_name, cn_id):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''insert into "Cities" values ({0},'{1}', '{2}')'''.format(cid, c_name, cn_id)
        res = cursor.execute(sql)
        self.conn.commit()

    def insert_cu(self, cid, uid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()

        sql1 = '''select 1 from "city_client" where city_id = {0} and client_id = {1}'''.format(cid, uid)
        cursor.execute(sql1)
        res = cursor.fetchall()
        if not res:
            sql2 = '''insert into "city_client" (city_id, client_id) values ({0},{1})'''.format(cid, uid)
            cursor.execute(sql2)
        self.conn.commit()

    def delete_cu(self, cid, uid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''delete from "city_client" where city_id = {0} and client_id = {1}'''.format(cid, uid)
        cursor.execute(sql)
        self.conn.commit()

    def getCityNamesForUser(self, uid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''select distinct C.city_name from "Cities" C inner join city_client cc on C.c_id = cc.city_id where client_id = {0}'''.format(uid)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        return res

    def getCitiesForUser(self, uid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''select distinct C.city_name, C.c_id from "Cities" C inner join city_client cc on C.c_id = cc.city_id where client_id = {0}'''.format(uid)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        return res

    def cityName(self, cid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()
        sql = '''select city_name from "Cities" where c_id = {0}'''.format(cid)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.conn.commit()
        return res[0][0]

    def finduc(self, cid, uid):
        self.conn.autocommit = True
        cursor = self.conn.cursor()

        sql1 = '''select 1 from "city_client" where city_id = {0} and client_id = {1}'''.format(cid, uid)
        cursor.execute(sql1)
        res = cursor.fetchall()
        if res:
            return True
        else:
            return False

    def close(self):
        self.conn.close()
