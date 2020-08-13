from server import Server
from config import api_token, vk_group_id


server1 = Server(api_token, vk_group_id, "server1")

server1.start()
