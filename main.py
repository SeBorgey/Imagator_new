"""\file main.py

    Основной цикл работы программы: общение с пользователем и запуск нейросетей.
"""
import os
from io import BytesIO

import torchvision.transforms as transforms
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton
from aiogram.types.message import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

import config
from inference_esrgan import run_super_res
from net import run_style_transfer, unloader, download_cnn
from users import create_user_checker, users
import language


## Создание экземпляров бота, диспетчера, конечного автомата и загрузка обученной модели VGG19
print('Bot is starting..')
cnn = download_cnn()
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
print('Bot has been started')
admin = 189590002


class Form(StatesGroup):
    report = State()


"""\brief Отзыв

    Бот просит у пользователя в следующем сообщении оставить отзыв.   
"""
@dp.message_handler(commands=['report'])
async def report(message):
    create_user_checker(message.from_user.id)
    await Form.report.set()
    await message.reply(users[message.from_user.id].l.report)


"""\brief Отмена отзыва

    Возможность отмены оставления отзыва.
"""
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК')


"""\brief Отмена отзыва

    Функция добавляет вариант отмены отзыва на английском. 
"""
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК')


"""\brief Отправка отзыва

    Бот отправляет отзыв пользователя админу. 
"""
@dp.message_handler(state=Form.report)
async def process_name(message: types.Message, state: FSMContext):
    await bot.send_message(admin, message.text)
    await state.finish()


"""\brief Помощь

    Вывод списка команд бота. 
"""
@dp.message_handler(commands=['help'])
async def def_help(message):
    create_user_checker(message.from_user.id)
    await bot.send_message(message.chat.id, users[message.from_user.id].l.help)


"""\brief Старт.

    Запуск основного цикла работы. Бот представляется и даёт пользователю выбор о том, что бот должен сделать.
"""
@dp.message_handler(commands=['start'])
async def welcome(message):
    create_user_checker(message.from_user.id)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    item1 = InlineKeyboardButton(users[message.from_user.id].l.style_transfer, callback_data='yes')
    item2 = InlineKeyboardButton(users[message.from_user.id].l.super_res, callback_data='no')

    inline_keyboard.add(item1, item2)
    me = await bot.get_me()
    text = (users[message.from_user.id].l.hello +
            message.from_user.first_name + ". " +
            users[message.from_user.id].l.i +
            me.first_name +
            users[message.from_user.id].l.start)
    await bot.send_message(message.chat.id, text,
                           parse_mode=ParseMode.MARKDOWN,
                           reply_markup=inline_keyboard)


"""\brief Сброс.

    Удаление экземпляра пользователя. Удаление всех его фото.
"""
@dp.message_handler(commands=['reset'])
async def def_reset(message):
    create_user_checker(message.from_user.id)  # Чтобы не выдало ошибку при отсутствии экземпляра

    if os.path.exists(f'images/{message.from_user.id}' + '_style_photo.pickle'):
        os.remove(f'images/{message.from_user.id}' + '_style_photo.pickle')

    if os.path.exists(f'images/{message.from_user.id}' + '_bad_photo.pickle'):
        os.remove(f'images/{message.from_user.id}' + '_bad_photo.pickle')

    if os.path.exists(f'images/{message.from_user.id}' + '_content_photo.pickle'):
        os.remove(f'images/{message.from_user.id}' + '_content_photo.pickle')

    if os.path.exists(f'images/{message.from_user.id}' + '_result.png'):
        os.remove(f'images/{message.from_user.id}' + '_result.png')

    if os.path.exists(f'images/{message.from_user.id}' + '_super_result.png'):
        os.remove(f'images/{message.from_user.id}' + '_super_result.png')

    await bot.send_message(message.chat.id, users[message.from_user.id].l.reset)
    users.pop(message.from_user.id)


"""\brief Русский язык.

    Включение русского языка.
"""
@dp.message_handler(commands=['ru'])
async def turn_ru(message):
    create_user_checker(message.from_user.id)
    users[message.from_user.id].l = language.Rus()

    await bot.send_message(message.chat.id, users[message.from_user.id].l.turn_lang)

"""\brief Русский язык.

    Включение английского языка.
"""
@dp.message_handler(commands=['eng'])
async def turn_eng(message):
    create_user_checker(message.from_user.id)
    users[message.from_user.id].l = language.Eng()

    await bot.send_message(message.chat.id, users[message.from_user.id].l.turn_lang)


"""\brief Приём картинок

    Функция проверяет, приём для какого вида работ активирован. Дальше смотрит, какая по счёту картинка, если все
    картинки приняты, то запускает нейросеть.
"""
@dp.message_handler(content_types=['photo'])
async def get_photo(message):
    create_user_checker(message.from_user.id)

    if users[message.from_user.id].is_getting_transfer:

        if message.media_group_id:
            users[message.from_user.id].group_counter += 1

            if users[message.from_user.id].group_counter == 1:
                await bot.send_message(message.chat.id, users[message.from_user.id].l.only_one)

            return

        try:
            photo = message.photo[-1]
            photo_id = message.photo[-1].file_id
            photo_width = message.photo[-1].width
            photo_height = message.photo[-1].height
            file = await bot.get_file(photo_id)

        except IndexError:
            await bot.send_message(message.chat.id, users[message.from_user.id].l.error)
            return

        if users[message.from_user.id].counter == 0:
            users[message.from_user.id].style_photo_size = (photo_width, photo_height)
            await photo.download(f'images/{message.from_user.id}' + '_style_photo.pickle')
            await bot.send_message(message.chat.id, users[message.from_user.id].l.ok_now_content)

        if users[message.from_user.id].counter == 1:
            users[message.from_user.id].content_photo_size = (photo_width, photo_height)
            await photo.download(f'images/{message.from_user.id}' + '_content_photo.pickle')
            users[message.from_user.id].is_getting_transfer = False
            users[message.from_user.id].counter = -1
            await bot.send_message(message.chat.id, users[message.from_user.id].l.receive_photo)
            await transfer_style(message)

        users[message.from_user.id].counter += 1

    if users[message.from_user.id].is_getting_quality:
        if message.media_group_id:
            users[message.from_user.id].group_counter += 1
            if users[message.from_user.id].group_counter == 1:
                await bot.send_message(message.chat.id, users[message.from_user.id].l.only_one)
            return
        try:
            photo = message.photo[-1]
            photo_id = message.photo[-1].file_id
            photo_width = message.photo[-1].width
            photo_height = message.photo[-1].height
            file = await bot.get_file(photo_id)

        except IndexError:
            await bot.send_message(message.chat.id, users[message.from_user.id].l.error)
            return
        if photo_width > 500 or photo_height > 500:
            await bot.send_message(message.chat.id, users[message.from_user.id].l.reject)
            return
        users[message.from_user.id].bad_photo_size = (photo_width, photo_height)
        await photo.download(f'images/{message.from_user.id}' + '_bad_photo.pickle')
        users[message.from_user.id].is_getting_quality = False
        await bot.send_message(message.chat.id, users[message.from_user.id].l.receive_photo)
        await super_res(message)

    elif message.media_group_id and users[message.from_user.id].not_instructed_counter < 1:
        users[message.from_user.id].not_instructed_counter += 1
        await welcome(message)


"""\brief Выбор

    Функция для понимания, чего хочет пользователь: трансферстайл или апскейлинг.
"""
@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    create_user_checker(call.from_user.id)

    if call.message:
        if call.data == 'yes':
            users[call.from_user.id].is_getting_transfer = True
            await bot.send_message(call.message.chat.id, users[call.from_user.id].l.ok_send_style)
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                message_id=call.message.message_id,
                                                reply_markup=None)
        elif call.data == 'no':
            users[call.from_user.id].is_getting_quality = True
            await bot.send_message(call.message.chat.id, users[call.from_user.id].l.ok_send_res)
            await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                message_id=call.message.message_id,
                                                reply_markup=None)


"""\brief Перенос стиля

    Запсук нейросети переноса стиля. Полученное изображение возвращается к разрешению контента и отправляется
    пользователю после этого высвечивается запрос о том, как дальше продолжать работу.
"""
async def transfer_style(message):
    output = run_style_transfer(cnn,
                                f'images/{message.from_user.id}',
                                users[message.from_user.id].style_photo_size,
                                users[message.from_user.id].content_photo_size,
                                )

    output = unloader(output)
    a = config.imsize
    b = config.imsize
    c = list(users[message.from_user.id].content_photo_size)[0]
    d = list(users[message.from_user.id].content_photo_size)[1]

    coefX = c / a
    coefY = d / b

    unloader1 = transforms.Resize((int(config.imsize * coefY + 0.5), int(config.imsize * coefX + 0.5)))
    output = unloader1(output)

    bio = BytesIO()
    bio.name = f'images/{message.from_user.id}+_result.png'
    output.save(bio, 'PNG')
    bio.seek(0)

    await bot.send_photo(message.chat.id, bio, users[message.from_user.id].l.here_it_is)

    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    item1 = InlineKeyboardButton(users[message.from_user.id].l.style_transfer, callback_data='yes')
    item2 = InlineKeyboardButton(users[message.from_user.id].l.super_res, callback_data='no')
    inline_keyboard.add(item1, item2)

    await bot.send_message(message.chat.id, users[message.from_user.id].l.resume,
                           reply_markup=inline_keyboard)


"""\brief Увеличение разрешения

    Запускается нейросеть для увеличения полученного изображения с сохранением качества. Изображение отправляется
    пользователю. Далее высвечивается запрос о том, как дальше продолжать работу.
"""
async def super_res(message):
    run_super_res(message)
    with open(f'images/{message.from_user.id}+_super_result.png', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, users[message.from_user.id].l.here_it_is)

    os.remove(f'images/{message.from_user.id}+_super_result.png')
    os.remove(f'images/{message.from_user.id}' + '_bad_photo.pickle')
    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    item1 = InlineKeyboardButton(users[message.from_user.id].l.style_transfer, callback_data='yes')
    item2 = InlineKeyboardButton(users[message.from_user.id].l.super_res, callback_data='no')
    inline_keyboard.add(item1, item2)

    await bot.send_message(message.chat.id, users[message.from_user.id].l.resume,
                           reply_markup=inline_keyboard)


if __name__ == "__main__":
    executor.start_polling(dp)
