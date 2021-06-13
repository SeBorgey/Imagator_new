from io import BytesIO

# import torch
import torchvision.transforms as transforms
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton
from aiogram.types.message import ParseMode
from aiogram.utils import executor

import config
from net import run_style_transfer, unloader, download_cnn
from users import create_user_checker, users

print('Bot is starting..')
cnn = download_cnn()
bot = Bot(token=config.TTOKEN)
dp = Dispatcher(bot)
print('Bot has been started')
# print(torch.cuda.is_available())


async def empty_function():
    pass


@dp.message_handler(commands=['start', 'help'])
async def welcome(message):
    try:
        create_user_checker(message.from_user.id)

        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        item1 = InlineKeyboardButton("Давай!", callback_data='yes')
        item2 = InlineKeyboardButton("Чуть позже", callback_data='no')

        inline_keyboard.add(item1, item2)
        me = await bot.get_me()

        await bot.send_message(message.chat.id, f'Приветствую тебя, *{message.from_user.first_name}*! '
                                                f'Я *{me.first_name}* — бот, созданный, чтобы '
                                                f'переносить стиль одних фотографий на другие. '
                                                f'Начнем?',
                               parse_mode=ParseMode.MARKDOWN,
                               reply_markup=inline_keyboard)
    except Exception as e:
        await message.reply(message, "Ошибка: " + repr(e))


@dp.message_handler(commands=['transfer_style'])
async def transfer(message):
    try:

        create_user_checker(message.from_user.id)

        inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Давай!", callback_data='yes')
        item2 = types.InlineKeyboardButton("Чуть позже.", callback_data='no')

        inline_keyboard.add(item1, item2)

        await bot.send_message(message.chat.id, f'Итак, начнем?',
                               parse_mode='Markdown',
                               reply_markup=inline_keyboard)

    except Exception as e:
        await message.reply(message, "Ошибка: " + repr(e))


@dp.message_handler(content_types=['photo'])
async def get_photo(message):
    # try:
    create_user_checker(message.from_user.id)

    if users[message.from_user.id].is_getting_photos:

        if message.media_group_id:
            users[message.from_user.id].group_counter += 1

            if users[message.from_user.id].group_counter == 1:
                await bot.send_message(message.chat.id, 'Пожалуйста, отправляйте только по одному фото в сообщении')

            return

        try:
            photo = message.photo[-1]

            photo_id = message.photo[-1].file_id
            photo_width = message.photo[-1].width
            photo_height = message.photo[-1].height

            file = await bot.get_file(photo_id)

        except IndexError:
            await bot.send_message(message.chat.id, 'Ошибка. Попробуй отправить то же фото еще раз')
            return

        if users[message.from_user.id].counter == 0:
            users[message.from_user.id].style_photo_size = (photo_width, photo_height)
            await photo.download(f'\images\{message.from_user.id}' + '_style_photo.pickle')

            # with open(f'images/{message.from_user.id}' + '_style_photo.pickle', 'wb') as file:
            #     file.write(users[message.from_user.id].style_photo)

            await bot.send_message(message.chat.id, 'Отлично, теперь отправьте фото контента')

        if users[message.from_user.id].counter == 1:
            users[message.from_user.id].content_photo_size = (photo_width, photo_height)
            await photo.download(f'\images\{message.from_user.id}' + '_content_photo.pickle')

            # with open(f'images/{message.from_user.id}' + '_content_photo.pickle', 'wb') as file:
            #     file.write(users[message.from_user.id].content_photo)

            users[message.from_user.id].is_getting_photos = False
            users[message.from_user.id].counter = -1
            await bot.send_message(message.chat.id, 'Фото получил, начинаю работу!')
            await transfer_style(message)

        users[message.from_user.id].counter += 1

    elif message.media_group_id and users[message.from_user.id].not_instructed_counter < 1:
        users[message.from_user.id].not_instructed_counter += 1
        await welcome(message)

    # except Exception as e:
    #     bot.reply_to(message, "Ошибка: "+repr(e))


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    create_user_checker(call.from_user.id)

    if call.message:
        if call.data == 'yes':
            users[call.from_user.id].is_getting_photos = True

            await bot.send_message(call.message.chat.id, 'Отлично, тогда отправь мне сначала фото стиля, '
                                                         'а затем фото контента. Жду!')
        elif call.data == 'no':
            await bot.send_message(call.message.chat.id, 'Хорошо, пиши, как понадоблюсь!')

        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)


async def transfer_style(message):
    output = run_style_transfer(cnn,
                                f'\images\{message.from_user.id}',
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
    bio.name = f'\images\{message.from_user.id}+_result.png'
    output.save(bio, 'PNG')
    bio.seek(0)

    await bot.send_photo(message.chat.id, bio, 'Вот, что у меня получилось')

    inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
    item1 = InlineKeyboardButton("Давай!", callback_data='yes')
    item2 = InlineKeyboardButton("Чуть позже", callback_data='no')
    inline_keyboard.add(item1, item2)

    await bot.send_message(message.chat.id, f'Хочешь перенести стиль еще на одну фотографию?',
                           reply_markup=inline_keyboard)


if __name__ == "__main__":
    executor.start_polling(dp)

