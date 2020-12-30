import random
import requests

import sqlite3 as sql
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from config import vk_group_id, api_token
from database import Database


class Server:

    def __init__(self, token, group_id, server_name: str = "Empty"):

        self.server_name = 'vk_bot_server'

        self.vk = vk_api.VkApi(token=api_token)

        # Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, vk_group_id)

        self.vk_api = self.vk.get_api()

    def send_msg(self, send_id, message, keyboard_type="default"):
        """Отправляет заданное сообщение(message)
           пользователю с заданным id(send_id)
           keyboard_type - тип клавиатуры, отображаемой у пользователя

        """
        return self.vk_api.messages.send(
            peer_id=send_id,
            random_id=random.getrandbits(64),
            message=message,
            keyboard=open(
                f"keyboards\{keyboard_type}.json", "r",
                encoding="UTF-8"
                ).read()
            )

    def get_first_name(self, user_id):
        """Возвращает имя пользователя по его id

        """
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def bot_logic(self, dict1, dict2, user_id, msg_text):
        try:
            result = self.send_msg(
                user_id,
                dict1[f"{msg_text}"],
                dict2[f"{msg_text}"]
                )
        except KeyError:
            result = self.send_msg(user_id, "Такой команды нет!", "default")
        return result

    def start(self):

        Database().start_db()

        pricing = "Общий зал:\n 1 час - 120 рублей\n \
            3 часа - 270 рублей\n 5 часов - 400 рублей\n \
            Ночной пакет - 500 рублей\nVIP:\n 1 час - 200 рублей\n \
            3 часа - 500 рублей\n \
            5 часов - 750 рублей\n Ночной пакет - 1000 рублей\n \
            Консоли(общая зона/LG Cinebeam):\n \
            1 час - 300/500 рублей\n 3 часа - 700/1200 рублей"

        pc_configuration = "ОБЩИЙ ЗАЛ:\n Процессор: Intel Core i5-9600k\n \
            Видеокарта: NVIDIA GeForce RTX 2060 Super\n \
            Оперативная память: 16 GB\n \
            Накопители: HDD 1Tb + SSD 512 Gb\n \
            Монитор: LG 27GK750F (27', 240 Гц)\n \
            VIP КОМНАТЫ:\n Процессор: Intel Core i7-9700k\n \
            Видеокарта: NVIDIA GeForce RTX 2080 Super\n \
            Оперативная память: 16 GB\n \
            Накопители: HDD 1Tb + SSD 512 Gb\n \
            Монитор: LG 27GK750F (27', 240 Гц)\n\
            ПЕРИФЕРИЯ:\n Мышь: Razer DeathAdder Elite\n \
            Клавиатура: Razer BlackWidow\n \
            Коврик: Razer Goliathus XL\n \
            Гарнитура: Razer Kraken TE\n \
            Держатель провода для мыши: Razer Bungee V2"

        # Слушаем действия пользователй

        for event in self.long_poll.listen():

            if event.type == VkBotEventType.MESSAGE_NEW:

                # Если пришло сообщение
                # message - сообщение как объект
                # from_id - id пользователя от которого пришло сообщение
                # text - тело сообщения
                # username - имя пользователя
                # match_id_text - проверка на наличие пользователя в БД
                # match_accept_text - проверка подписан ли пользователь
                # commands_keybrd - словарь клавиатур
                # commands_text - словарь ответов пользователю

                message = event.obj['message']
                from_id = message['peer_id']
                text = message['text']
                username = self.get_first_name(from_id)
                match_id_text = Database().compare_id(from_id)
                match_accept_text = Database().compare_isUserAccept(from_id)
                commands_keybrd = {
                    "В начало": "default",
                    "Команды": "commands",
                    "Наши цены": "commands",
                    "Железо": "commands",
                    "Начать": "accepting",
                    "Подписаться на рассылку": "default",
                    "!stop": "accepting"
                    }

                commands_text = {
                    "Начать": f"Привет, {username}!\n\
                        Для начала необходимо подписаться на рассылку",
                    "В начало": "Возвращаюсь в начало",
                    "Команды": "Смотри",
                    "Наши цены": pricing,
                    "Железо": pc_configuration,
                    "Подписаться на рассылку": "Вы подписаны!",
                    "!stop": "Вы отписались!"
                    }

                # Выводит на консоль от кого пришло сообщение,
                # Его текст и его тип(от пользователя или от группы)

                print("Username: " + username)
                print("Text: " + text)
                print("Type: ", end="")
                if from_id > 0:
                    print("private message")
                else:
                    print("group message")
                print(" --- ")

                # Логика бота

                self.bot_logic(commands_text, commands_keybrd, from_id, text)

                if text == "Подписаться на рассылку":
                    # Если получено сообщение 'Подписаться на рассылку'
                    # То проверяет есть ли в БД запись с таким id
                    # Если да, то именяет isUSerAccept на 1
                    # Если нет, то создает новую запись
                    if f"{from_id}" == match_id_text:
                        Database().subscribe(from_id)
                    else:
                        Database().new_user(from_id)
                elif text == "!stop" and f"{from_id}" == match_id_text:
                    # Если получено сообщение '!stop'
                    # То отписывает пользователя от рассылки
                    # Не удаляя его id из БД.
                    Database().unsubscribe(from_id)


