"""\file users.py

    Структура данных, где
    users - словарь, у которого ключи - это id пользователей. Значения - это флаги и настройки конкретного пользователя.
    Данная структура позволяет общаться сразу с несколькими пользователями и помнить, какой этап работы у какого
    пользователя происходит в данный момент. Также структура позволяет общаться с каждым пользователем на языке,
    который он выберет.
"""
import language
users = {}


class Checker:
    is_getting_transfer = False
    counter = 0
    group_counter = 0
    style_photo_size = (0, 0)
    content_photo_size = (0, 0)
    bad_photo_size = (0, 0)
    not_instructed_counter = 0
    is_getting_quality = False
    l = language.Rus()

    def __init__(self):
        pass


"""\brief Проверка и создание экземпляра пользователя

    При приёме любого сообщения проверяется существование экземпляра в словаре. В случае отсутствия он создаётся 
    со всеми служебными переменными. В дальнейшем эти переменные используются для корректной работы с пользователем.
    Можно сбросить всю работу с ботом, удалив свой экземпляр из словаря. Для этого необходимо подать команду reset.
"""
def create_user_checker(userid):
    global users
    if userid in users.keys():
        return
    param = Checker()
    new_user = {userid: param}
    users.update(new_user)
