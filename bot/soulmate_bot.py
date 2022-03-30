import telebot
from telebot import types
from .bot_utils import TOKEN

sm_bot = telebot.TeleBot(TOKEN)


def is_in_base(user):
    return not user


@sm_bot.message_handler(commands=['start'])
def start(message):
    sm_bot.send_message(message.chat.id, 'Привет, я бот для знакомств')
    btns = types.InlineKeyboardMarkup()
    if not is_in_base(message.chat.id):
        create_acc = types.InlineKeyboardButton("Завести анкету", callback_data='create')
        not_create_acc = types.InlineKeyboardButton("Ne Завести анкету", callback_data='not_create')
        btns.add(create_acc)
        btns.add(not_create_acc)
        sm_bot.send_message(message.chat.id, 'Ты тут впервые, хочешь завести анкету?', reply_markup=btns)


@sm_bot.callback_query_handler(func=lambda call: call.data == 'create')
def register(call):
    sm_bot.send_message(call.message.chat.id, 'Коротко расскажи о себе')
