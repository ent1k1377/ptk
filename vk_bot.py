import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import sqlite3


def main():
    TOKEN = 'cdbf3250db7404d91e4e88c7834ba2b587c9f60016bc02ff9ad7da18fbcf4008f1f7b9ff1ea6303195f29'
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, 194118559)
    conn = sqlite3.connect("db/ptk.db")
    cursor = conn.cursor()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            message = event.obj.message['text'].split()
            result = cursor.execute("SELECT g.'group' FROM groups as g").fetchall()
            db = []
            for i in result:
                db.append(i[0])
            if message[0] == '/unset':
                text = f"Вы отписались"
                cursor.execute(
                    f'DELETE FROM vk_db WHERE "id_dialog" = {event.obj.message["from_id"]}')
                conn.commit()
            elif message[0] == '/set' and len(message) == 2 and str(message[1]).isdigit():
                if message[1] in db:
                    text = f"Все хорошо,  теперь вы привязаны к группе {message[1]}"
                    cursor.execute(
                        f'DELETE FROM vk_db WHERE "id_dialog" = {event.obj.message["from_id"]}')
                    conn.commit()
                    cursor.execute(f"""INSERT INTO vk_db('id_dialog' ,'group')
                                        VALUES ({event.obj.message['from_id']}, 
                                        {message[1]})""")
                    conn.commit()
                else:
                    text = f"Такой группы не существует, можно выбрать {', '.join([i for i in db])}."
            else:
                text = "Вы неправильно задали параметр"
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=text,
                             random_id=random.randint(0, 2 ** 64))


main()
