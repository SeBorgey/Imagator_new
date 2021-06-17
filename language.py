"""\file language.py

    Контейнер для языков.
"""
class Rus:
    style_transfer = "Перенести стиль"
    super_res = "Повысить разрешение"
    hello = "Приветствую тебя, "
    i = "Я "
    start = ". Я умею повышать разрешение фотографий и переносить стиль одних фотографий на другие. Начнем?"
    only_one = "Нет, отправляй фото по одному"
    ok_now_content = "Отлично, теперь отправь фото контента"
    receive_photo = "Фото получил, начинаю работу!"
    error = "Ошибка. Попробуй отправить то же фото еще раз"
    ok_send_style = "Отлично, тогда отправь мне сначала фото стиля, а затем фото контента. Жду!"
    ok_send_res = "Отлично, тогда отправь мне фото, разрешение которого хочешь повысить. " \
                  "Разрешение исходного фото не должно превышать 500х500"
    here_it_is = "Вот, что у меня получилось"
    resume = "Продолжить работу?"
    turn_lang = "Включен русский язык"
    report = "Следующим сообщением напиши свой отзыв о боте"
    help = "Список команд \n" \
           "/start Начало работы\n" \
           "/help Список команд\n"\
           "/report Оставить отзыв\n" \
           "/cancel Отмена отзыва\n" \
           "/ru Русский язык\n" \
           "/eng English lang\n" \
           "/reset Сброс по умолчанию"
    reject = "Фото слишком большое, разрешение должно быть меньше 500"
    reset = "Бот сброшен"

    def __init__(self):
        pass


class Eng:
    style_transfer = "Style transfer"
    super_res = "Super resolution"
    hello = "Hi, "
    i = "I am "
    start = ". I can upscale pictures and transfer style of one picture to another. Let's start?"
    only_one = "Please, send pictures one by another"
    ok_now_content = "OK, now send me content picture"
    receive_photo = "Picture was recieved. Getting start work"
    error = "Error. Try to send picture again"
    ok_send_style = "Great, then send me a picture of the style first, then a picture of the content. I'm waiting!"
    ok_send_res = "Great, then send me the picture you want to upgrade. " \
                  "The resolution of the original photo should not exceed 500x500"
    here_it_is = "That's what I did"
    resume = "Resume?"
    turn_lang = "Switched to English"
    report = "Use the following message to write your feedback about the bot"
    help = "Command List \n" \
           "/start Getting started\n" \
           "/help Command List\n" \
           "/report Give feedback\n" \
           "/cancel Cancel feedback\n" \
           "/ru Русский язык\n" \
           "/eng English lang\n" \
           "/reset Reset to default"
    reject = "This picture is too big. Resolution must be less than 500"
    reset = "Bot was reset"

    def __init__(self):
        pass
