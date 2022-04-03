import telebot
from telebot import types
from .bot_utils import TOKEN

bot = telebot.TeleBot(TOKEN)


def is_in_base(user):
    return not user


def write_to_base(name):
    pass


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, я бот для знакомств')
    btns = types.InlineKeyboardMarkup()
    if not is_in_base(message.chat.id):
        create_acc = types.InlineKeyboardButton("Завести анкету", callback_data='create')
        not_create_acc = types.InlineKeyboardButton("Ne Завести анкету", callback_data='not_create')
        btns.add(create_acc)
        btns.add(not_create_acc)
        bot.send_message(message.chat.id, 'Ты тут впервые, хочешь завести анкету?', reply_markup=btns)


@bot.callback_query_handler(func=lambda call: call.data == 'create')
def register(call):
    bot.send_message(call.message.chat.id, 'Для начала представься. Как тебя зовут?')
    bot.register_next_step_handler(call.message, get_name)


def get_name(message):
    write_to_base(message.text)
    bot.send_message(message.chat.id, f'Добро пожаловать, {message.text}. Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    write_to_base(message.text)
    bot.send_message(message.chat.id, 'Теперь коротко расскажи о себе что угодно, это будет твоим описанием')
    bot.register_next_step_handler(message, get_desc)


def get_desc(message):
    write_to_base(message.text)
    bot.send_message(message.chat.id, 'Ну и наконец прикрепи свою фотку')
