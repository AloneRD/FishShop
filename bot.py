from math import prod
import os
from pydoc import doc
import api
import redis

from dotenv import load_dotenv
from functools import partial

from telegram.ext import Filters, Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None


def start(bot, update, user_data, access_token_cms):
    """
    Хэндлер для состояния START.

    Бот отвечает пользователю фразой "Привет!" и переводит его в состояние ECHO..
    """
    products = api.get_products(access_token_cms)['data']
    user_data['products'] = products
    keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id']) for product in products]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Добро пожаловать к нам в магазин!!',
                              reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(bot, update, user_data, access_token_cms):
    print(update.callback_query.data)
    product_id = update.callback_query.data
    response_get_product = api.get_product(access_token_cms, product_id)
    product = response_get_product['data']
    product_image_id = product['relationships']['main_image']['data']['id']
    image = api.get_image_product(access_token_cms, product_image_id)
    image_link = image['data']['link']['href']

    keyboard = [[InlineKeyboardButton('Назад', callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text_blocks = [f"{product['name']}\n",
                   f"{product['meta']['display_price']['with_tax']['formatted']} per kg \n",
                   f"{product['description']}\n"]

    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id

    bot.send_photo(chat_id=chat_id, photo=image_link, caption='\n'.join(text_blocks), reply_markup=reply_markup)
    bot.delete_message(chat_id=chat_id, message_id=message_id)

    return "HANDLE_DESCRIPTION"


def handle_description(bot, update, user_data, access_token_cms):
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id
    user_reply = update.callback_query.data
    if user_reply == 'back':
        products = user_data['products']
        keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id']) for product in products]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=chat_id, text='Вы вернулись в главное меню',
                         reply_markup=reply_markup)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        return "HANDLE_MENU"


def handle_users_reply(bot, update, user_data, access_token_cms):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """

    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': partial(start, access_token_cms=access_token_cms),
        'HANDLE_MENU': partial(handle_menu, access_token_cms=access_token_cms),
        'HANDLE_DESCRIPTION': partial(handle_description, access_token_cms=access_token_cms)
    }
    state_handler = states_functions[user_state]
    print(state_handler)
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(bot, update, user_data)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        password_redis_db = os.getenv("REDIS_DB")
        redis_host = os.getenv("REDIS_HOST")
        _database = redis.Redis(host=redis_host, port=12655, db=0, password=password_redis_db)
    return _database


def main():
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    access_token_cms = api.get_access_token(client_id)
    # api.add_product_cart(dict(products['data'][0]), access_token)
    # api.get_cart(1, access_token)

    token = os.getenv("TG_TOKEN")

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(partial(handle_users_reply, access_token_cms=access_token_cms), pass_user_data=True))
    dispatcher.add_handler(MessageHandler(Filters.text, partial(handle_users_reply, access_token_cms=access_token_cms), pass_user_data=True))
    dispatcher.add_handler(CommandHandler('start', partial(handle_users_reply, access_token_cms=access_token_cms), pass_user_data=True))

    updater.start_polling()


if __name__ == '__main__':
    main()
