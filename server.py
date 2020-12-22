import vk_api
import sqlite3 as sql
import requests
import random
from vk_api.bot_longpoll import VkBotEventType
from vk_api.bot_longpoll import VkBotLongPoll
from config import vk_group_id, api_token


class Server:

    def __init__(self, token, group_id, server_name: str="Empty"):

        self.server_name = 'server1'

        self.vk = vk_api.VkApi(token=api_token)
        
        # Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, vk_group_id)
        
        self.vk_api = self.vk.get_api()

    def send_msg(self, send_id, message, keyboard_type = "default"):
        ''' Отправляет заданноое сообщение(message) пользователю с заданным id(send_id)
            keyboard_type - тип клавиатуры, которая отображается у пользователя '''
         return self.vk_api.messages.send(peer_id=send_id,random_id = random.getrandbits(64),message=message,keyboard=open(f"keyboards\{keyboard_type}.json", "r", encoding="UTF-8").read())
    
    
    def compare_isUserAccept(self, user_id):
        ''' Проверяет по id пользователя подписан ли он на рассылку
            Вовзращает 0 если не подписан, возвращает 1 если подписан '''
        con = sql.connect('acceptedIDs.db')
        cur = con.cursor()
        select_coloumn = "SELECT isUserAccept FROM acceptedIDs WHERE userID=?"
        cur.execute(select_coloumn, [(user_id)])
        matchAccept = cur.fetchall()
        cur.close()
        con.commit()
        return matchAccept

    def compare_id(self, user_id):
        ''' Проверяет id пользователя на наличие его в базе данных рассылки
            Возвращает все совпадения которые он нашел '''
        con = sql.connect('acceptedIDs.db')
        cur = con.cursor()
        select_coloumn = "SELECT userID FROM acceptedIDs WHERE userID=?"
        cur.execute(select_coloumn, [(user_id)])
        matchId = cur.fetchall()
        cur.close()
        con.commit()
        return matchId
        
    def delete_id(self, user_id):
        ''' Отключает пользователя от рассылки по его id '''
        con = sql.connect('acceptedIDs.db')
        cur = con.cursor()
        select_coloumn = "UPDATE acceptedIDs SET isUserAccept=0 WHERE userID=?"
        cur.execute(select_coloumn, [(user_id)])
        cur.close()
        con.commit()

    def get_first_name(self, user_id):
        """ Возвращает имя пользователя по его id """
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']    

    def start(self):

        con = sql.connect('acceptedIDs.db')
        with con:
            cur = con.cursor()

            # Если не существует БД подписавшихся на рассылку, то созадет ее. Со столбацами: _id - счетчик, userID - id пользователя ВК, isUserAccept - логический тип 0/1 (не подписан/подписан).
            
            cur.execute("CREATE TABLE IF NOT EXISTS 'acceptedIDs' (_id INTEGER PRIMARY KEY AUTOINCREMENT, userID INTEGER,isUserAccept INTEGER)")
            con.commit() 

        pricing = "Общий зал:\n 1 час - 120 рублей\n 3 часа - 270 рублей\n 5 часов - 400 рублей\nНочной пакет - 500 рублей\nVIP:\n 1 час - 200 рублей\n 3 часа - 500 рублей\n 5 часов - 750 рублей\n Ночной пакет - 1000 рублей\nКонсоли(общая зона/LG Cinebeam):\n 1 час - 300/500 рублей\n 3 часа - 700/1200 рублей"
        pc_configuration = "ОБЩИЙ ЗАЛ:\n Процессор: Intel Core i5-9600k\n Видеокарта: NVIDIA GeForce RTX 2060 Super\n Оперативная память: 16 GB\n Накопители: HDD 1Tb + SSD 512 Gb\n Монитор: LG 27GK750F (27', 240 Гц)\nVIP КОМНАТЫ:\n Процессор: Intel Core i7-9700k\n Видеокарта: NVIDIA GeForce RTX 2080 Super\n Оперативная память: 16 GB\n Накопители: HDD 1Tb + SSD 512 Gb\n Монитор: LG 27GK750F (27', 240 Гц)\nПЕРИФЕРИЯ:\n Мышь: Razer DeathAdder Elite\n Клавиатура: Razer BlackWidow\n Коврик: Razer Goliathus XL\n Гарнитура: Razer Kraken TE\n Держатель провода для мыши: Razer Bungee V2"
        
        # Слушаем действия пользователй

        for event in self.long_poll.listen():
            
             if event.type == VkBotEventType.MESSAGE_NEW:
                
                # Если пришло сообщение. from_id - id пользователя от которого пришло сообщение
                #                        text - тело сообщения, username - имя пользователя

                message = event.obj['message']
                from_id = message['peer_id']
                text = message['text']
                username = self.get_first_name(from_id)
                match_id_text = f"{self.compare_id(from_id)}"
                match_accept_text = f"{self.compare_isUserAccept(from_id)}"
                
                # Выводит на консоль от кого пришло сообщение, его текст и его тип(от пользователя или от группы)

                print("Username: " + username)
                print("Text: " + text)
                print("Type: ", end="")  
                if from_id > 0:
                    print("private message")
                else:
                    print("group message")
                print(" --- ")
                
                # Логика бота

                if text == "Начать":
                    self.send_msg(from_id, f"Привет, {username}! Для того, чтобы пользоваться командами, тебе нужно подписаться на рассылку", "null") and self.send_msg(from_id, "Ты в любой момент можешь отписаться просто написав сюда !stop", "accepting")
                if text == "Подписаться на рассылку":
                    if match_accept_text[2:-3] == "1":
                        # Проверяет подписан ли пользователь
                        self.send_msg(from_id, "Вы уже подписаны на рассылку!")
                    else:
                        # Если пользователь ранее подписался, а потом отписался, то обновляет его isUserAccept поле, иначе добавляет новую строку с его id.
                        self.send_msg(from_id, "Вы успешно подписались на рассылку!")
                        if f"{from_id}" == match_id_text[2:-3]:
                            cur.execute(f"UPDATE acceptedIDs SET isUserAccept=1 WHERE userID={from_id}")
                            con.commit()
                        else:
                            cur.execute(f"INSERT INTO 'acceptedIDs' (userID,isUserAccept) VALUES ({from_id},1)")
                            con.commit()
                elif text == "!stop" and f"{from_id}" == match_id_text[2:-3]:
                    # Если получено сообщение '!stop', то отписывает пользователя от рассылки, не удаляя его id из БД.
                    self.send_msg(from_id,"Вы успешно отписались от рассылки!","accepting")
                    self.delete_id(from_id)
                    
                elif text == "В начало" and f"{from_id}" == match_id_text[2:-3]:
                    self.send_msg(from_id,"Возвращаюсь в начало")
                elif text == "Команды" and f"{from_id}" == match_id_text[2:-3]:
                    self.send_msg(from_id,"Смотри","commands")
                elif text == "Наши цены" and f"{from_id}" == match_id_text[2:-3]:
                    self.send_msg(from_id,pricing,"commands")
                elif text == "Железо" and f"{from_id}" == match_id_text[2:-3]:
                    self.send_msg(from_id,pc_configuration,"commands")


