import os
import api
import redis
import re

from dotenv import load_dotenv
from functools import partial

from telegram.ext import Filters, Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None

BUTTON_CART = InlineKeyboardButton('Корзина', callback_data='cart')
BUTTON_BACK = InlineKeyboardButton('Назад', callback_data='back')


def start(bot, update, user_data, access_token_cms):
    """
    Хэндлер для состояния START.
    """
    products = api.get_products(access_token_cms)['data']
    user_data['products'] = products
    keyboard = [
        [InlineKeyboardButton(product['name'], callback_data=product['id']) for product in products]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        text='Добро пожаловать к нам в магазин!!',
        reply_markup=reply_markup
        )
    return "HANDLE_DESCRIPTION"


def handle_menu(bot, update, user_data, access_token_cms):
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id

    products = api.get_products(access_token_cms)['data']
    user_data['products'] = products
    keyboard = [
        [InlineKeyboardButton(product['name'], callback_data=product['id']) for product in products],
        [BUTTON_CART]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_text('Меню', reply_markup=reply_markup)
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    return "HANDLE_DESCRIPTION"


def handle_description(bot, update, user_data, access_token_cms):
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id
    user_reply = update.callback_query.data
    if 'kg' in user_reply:
        quantity = int(re.match(r'(\d)', user_reply).group(1))
        api.add_product_cart(user_data['product'],
                             access_token_cms,
                             quantity, chat_id)
        return "HANDLE_DESCRIPTION"
    elif user_reply == 'cart':
        view_cart(bot, update, user_data, access_token_cms)
        return 'CART'
    elif user_reply == 'back':
        handle_menu(bot, update, user_data, access_token_cms)
        "HANDLE_DESCRIPTION"
    product_id = user_reply
    response_get_product = api.get_product(access_token_cms, product_id)
    product = response_get_product['data']
    user_data['product'] = product

    product_image_id = product['relationships']['main_image']['data']['id']
    image = api.get_image_product(access_token_cms, product_image_id)
    image_link = image['data']['link']['href']

    keyboard = [
        [BUTTON_BACK],
        [
            InlineKeyboardButton('1кг', callback_data='1kg'),
            InlineKeyboardButton('5кг', callback_data='5kg'),
            InlineKeyboardButton('10кг', callback_data='10kg')
        ],
        [BUTTON_CART]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text_blocks = [f"{product['name']}\n",
                   f"{product['meta']['display_price']['with_tax']['formatted']} per kg \n",
                   f"{product['description']}\n"]

    bot.send_photo(
        chat_id=chat_id,
        photo=image_link,
        caption='\n'.join(text_blocks),
        reply_markup=reply_markup
        )
    bot.delete_message(chat_id=chat_id, message_id=message_id)

    return "HANDLE_DESCRIPTION"


def generate_cart(chat_id, access_token_cms):
    keyboard = [
        [
            InlineKeyboardButton('В меню', callback_data='handle_menu'),
            InlineKeyboardButton('Оплатить', callback_data='pay')
            ]
        ]
    cart = api.get_cart(chat_id, access_token_cms)
    total_price_cart = api.get_cart_total(chat_id, access_token_cms)
    products_cart = cart['data']
    message_block = []
    for product in products_cart:
        product_price = product['meta']['display_price']['with_tax']['unit']['formatted']
        product_price_cart = product['meta']['display_price']['with_tax']['value']['formatted']
        message = f'{product["name"]} \n'\
                  + f'{product["description"]}\n'\
                  + f'{product_price} per kg\n'\
                  + f'{product["quantity"]}kg in cart for {product_price_cart}\n\n' \
                  + f'Total: {total_price_cart}\n\n\n\n\n'
        message_block.append(message)
        product_delete_button = [
            InlineKeyboardButton(f'Убрать из корзины {product["name"]}', callback_data=f'delete_{product["id"]}')
            ]
        keyboard.append(product_delete_button)
    if not message_block:
        message_block = ["Ваша корзина пуста"]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return message_block, reply_markup


def view_cart(bot, update, user_data, access_token_cms):
    user_reply = update.callback_query.data
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id

    if user_reply == 'back' or user_reply == 'handle_menu':
        handle_menu(bot, update, user_data, access_token_cms)
        return "HANDLE_DESCRIPTION"
    elif 'delete' in user_reply:
        product_id = re.search(r'delete_(.*)', user_reply).group(1)
        api.remove_product_from_cart(chat_id, product_id, access_token_cms)
        message_block, reply_markup = generate_cart(chat_id, access_token_cms)
        bot.send_message(
            chat_id=chat_id,
            text='\n'.join(message_block),
            reply_markup=reply_markup
            )
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        return "CART"
    elif user_reply == 'pay':
        bot.send_message(
            chat_id=chat_id,
            text='Пришлите мне свой e-mail'
            )
        return "WAITING_EMAIL"

    message_block, reply_markup = generate_cart(chat_id, access_token_cms)
    bot.send_message(
        chat_id=chat_id,
        text='\n'.join(message_block),
        reply_markup=reply_markup
        )
    bot.delete_message(chat_id=chat_id, message_id=message_id)
    return "CART"


def waiting_email(bot, update, user_data, access_token_cms):
    email = update.message.text
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton('В меню', callback_data='handle_menu')]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    api.create_customer(str(chat_id), email, access_token_cms)
    bot.send_message(
        chat_id=chat_id,
        text=f'{email} сохранен',
        reply_markup=reply_markup
        )
    return 'HANDLE_MENU'


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
        'START': partial(
            start,
            access_token_cms=access_token_cms
            ),
        'HANDLE_MENU': partial(
            handle_menu,
            access_token_cms=access_token_cms
            ),
        'HANDLE_DESCRIPTION': partial(
            handle_description,
            access_token_cms=access_token_cms
            ),
        'CART': partial(
            view_cart,
            access_token_cms=access_token_cms
        ),
        'WAITING_EMAIL': partial(
            waiting_email,
            access_token_cms=access_token_cms)
    }
    state_handler = states_functions[user_state]
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
        _database = redis.Redis(
            host=redis_host,
            port=12655,
            db=0,
            password=password_redis_db
            )
    return _database


def main():
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    access_token_cms = api.get_access_token(client_id)

    token = os.getenv("TG_TOKEN")

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CallbackQueryHandler(
            partial(handle_users_reply, access_token_cms=access_token_cms),
            pass_user_data=True
            )
        )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text,
            partial(handle_users_reply, access_token_cms=access_token_cms),
            pass_user_data=True
            )
        )
    dispatcher.add_handler(
        CommandHandler(
            'start',
            partial(handle_users_reply, access_token_cms=access_token_cms),
            pass_user_data=True
            )
        )

    updater.start_polling()


if __name__ == '__main__':
    main()
