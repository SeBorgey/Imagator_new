users = {}


class Checker:
    is_getting_photos = False
    counter = 0
    group_counter = 0
    style_photo_size = (0, 0)
    content_photo_size = (0, 0)
    not_instructed_counter = 0

    def __init__(self):
        pass


def create_user_checker(userid):
    global users
    if userid in users.keys():
        return
    param = Checker()
    new_user = {userid: param}
    users.update(new_user)
