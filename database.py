import sqlite3 as sql


class Database:

    con = sql.connect("acceptedIDs.db")
    cur = con.cursor()

    def __init__(self):
        pass

    def start_db(self):
        """Если не существует БД подписавшихся на рассылку, то созадет ее.
        Со столбацами: _id - счетчик, userID - id пользователя ВК,
        isUserAccept - логический тип 0/1 (не подписан/подписан).
        
        """
        self.cur.execute("\
        CREATE TABLE IF NOT EXISTS 'acceptedIDs' (\
        _id INTEGER PRIMARY KEY AUTOINCREMENT, \
        userID INTEGER, \
        isUserAccept INTEGER \
        )")
        self.con.commit()

    def subscribe(self, user_id):
        """В строке с userID = id пользователя
        Присваивает ячейке isUserAccept единицу
        Тем самым подписывая пользователя на рассылку

        """
        self.cur.execute(f"\
        UPDATE acceptedIDs \
        SET isUserAccept=1 \
        WHERE userID={user_id} \
        ")
        self.con.commit()

    def unsubscribe(self, user_id):
        """В строке с userID = id пользователя
        Присваивает ячейке isUserAccept ноль
        Тем самым отписывая пользователя от рассылки

        """
        self.cur.execute(f"\
        UPDATE acceptedIDs \
        SET isUserAccept=0 \
        WHERE userID={user_id} \
        ")
        self.con.commit()

    def compare_isUserAccept(self, user_id):
        """ Проверяет по id пользователя подписан ли он на рассылку.
            Вовзращает 0 если не подписан, возвращает 1 если подписан

        """
        select_coloumn = "\
            SELECT isUserAccept \
            FROM acceptedIDs \
            WHERE userID=?"
        self.cur.execute(select_coloumn, [(user_id)])
        matchAccept = self.cur.fetchall()
        self.con.commit()
        match_accept_text = f"{matchAccept}"
        match_accept_format = match_accept_text[2:-3]
        return match_accept_format

    def compare_id(self, user_id):
        """Проверяет id пользователя на наличие его в базе данных рассылки.
           Возвращает все совпадения которые он нашел

        """
        select_coloumn = "\
            SELECT userID \
            FROM acceptedIDs \
            WHERE userID=?"
        self.cur.execute(select_coloumn, [(user_id)])
        matchId = self.cur.fetchall()
        self.con.commit()
        match_id_text = f"{matchId}"
        match_format = match_id_text[2:-3]
        return match_format

    def new_user(self, user_id):
        """Добавляет новую запись в базу данных с полями
        userID = id пользователя
        isUserAccept = 1(т.е подписан на рассылку)

        """
        self.cur.execute(f"\
        INSERT INTO 'acceptedIDs' \
        (userID,isUserAccept) VALUES ({user_id},1) \
        ")
        self.con.commit()
