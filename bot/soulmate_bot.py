import telebot
from telebot import types

from .bot_utils import TOKEN, DB_URL, FILEPATH
from .serializers import *
from .database import *

bot = telebot.TeleBot(TOKEN)
db = connect_to_db(DB_URL)


def save_photo(photo, user_id):
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    src = FILEPATH + str(user_id) + '.jpg'
    with open(src, 'bw+') as new_file:
        new_file.write(downloaded_file)
    return src


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, я бот для знакомств')
    btns = types.InlineKeyboardMarkup()
    if not is_in_base(db, message.from_user.id):
        create_acc = types.InlineKeyboardButton("Завести анкету", callback_data='create')
        btns.add(create_acc)
        bot.send_message(message.chat.id, 'Ты тут впервые, хочешь завести анкету?', reply_markup=btns)
    else:
        update_acc = types.InlineKeyboardButton('Редактировать анкету', callback_data='update')
        search = types.InlineKeyboardButton('Продолжить искать людей', callback_data='search')
        show = types.InlineKeyboardButton('Посмотреть мою анкету', callback_data='show')
        btns.add(update_acc)
        btns.add(search)
        btns.add(show)
        bot.send_message(message.chat.id, "У тебя уже есть анкета, хочешь ее отредактировать?", reply_markup=btns)


@bot.callback_query_handler(func=lambda call: call.data == 'show')
def show_acc(call):
    user = db.Users.find_one({'tg_id': call.message.chat.id})
    bot.send_photo(call.message.chat.id, photo=open(user['img'], 'rb'), caption=generate_caption(user))


@bot.callback_query_handler(func=lambda call: call.data == 'create')
def register(call):
    bot.send_message(call.message.chat.id, 'Для начала представься. Как тебя зовут?')
    user = create_user()
    bot.register_next_step_handler(call.message, get_name, user)


def get_name(message, user):
    user['name'] = message.text
    user['tg_id'] = message.from_user.id
    bot.send_message(message.chat.id, f'Добро пожаловать, {message.text}. Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age, user)


def get_age(message, user):
    if type(message.text) == str:
        try:
            user['age'] = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, 'Впиши возраст цифрами, пожалуйста')
            bot.register_next_step_handler(message, get_age, user)
        else:
            bot.send_message(message.chat.id, 'Теперь коротко расскажи о себе что угодно, это будет твоим описанием')
            bot.register_next_step_handler(message, get_desc, user)
    else:
        bot.send_message(message.chat.id, 'Ты че ебанулся что это за хуйня?')
        bot.register_next_step_handler(message, get_age, user)


def get_desc(message, user):
    user['description'] = message.text
    bot.send_message(message.chat.id, 'Ну и наконец прикрепи свою фотку')
    bot.register_next_step_handler(message, get_photo, user)


def get_photo(message, user):
    if message.photo is None:
        bot.send_message(message.chat.id, 'Тебе нужно отправить фотграфию')
        bot.register_next_step_handler(message, get_photo, user)
    else:
        user['img'] = save_photo(message.photo[-1], message.from_user.id)
        add_user_to_base(db, user)
        btns = types.InlineKeyboardMarkup()
        show = types.InlineKeyboardButton("Посмотреть анкету", callback_data='show')
        btns.add(show)
        bot.send_message(message.chat.id, "Отлично, регистрация завершена!", reply_markup=btns)
