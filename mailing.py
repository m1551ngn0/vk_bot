from server import Server
from config import api_token, vk_group_id
import sqlite3 as sql

server1=Server(api_token, vk_group_id, "server1")

con = sql.connect('acceptedIDs.db')
cur = con.cursor()
cur.execute("SELECT Count(*) FROM acceptedIDs")
result = cur.fetchall()
result_text = f"{result}"
cyf = int(result_text[2:-3])
con.commit() 




i = 0
while i < cyf:
    sendsDenied = 0
    sendsAccepts = 0
    i = i + 1
    uid = i
    con = sql.connect('acceptedIDs.db')
    cur = con.cursor()
    cur.execute(f"SELECT userID FROM acceptedIDs WHERE _id={uid}")
    semiresult = cur.fetchall()
    cur.close()
    con.commit()
    semiresult_text = f"{semiresult}"
    match = int(semiresult_text[2:-3])
    compare_result = f"{server1.compare_isUserAccept(match)}"
    if compare_result[2:-3] == "1":
        server1.send_msg(match,"Пробная рассылка")
        sendsAccepts = sendsAccepts + 1
    else:
        sendsDenied = sendsDenied + 1
print(f"Пользователей получивших рассылку - {sendsAccepts}\nПользователей которые отписались - {sendsDenied}")