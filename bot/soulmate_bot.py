import telebot
from bson.objectid import ObjectId
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
    btns = types.InlineKeyboardMarkup(row_width=2)
    if not is_in_base(db, message.from_user.id):
        create_acc = types.InlineKeyboardButton("Завести анкету", callback_data='create')
        btns.add(create_acc)
        bot.send_message(message.chat.id, 'Ты тут впервые, хочешь завести анкету?', reply_markup=btns)
    else:
        update_account = types.InlineKeyboardButton('Редактировать анкету', callback_data='update')
        search_ = types.InlineKeyboardButton('Продолжить искать людей', callback_data='search')
        show = types.InlineKeyboardButton('Посмотреть мою анкету', callback_data='show')
        btns.add(update_account, search_, show)
        bot.send_message(message.chat.id, "У тебя уже есть анкета, хочешь ее отредактировать?", reply_markup=btns)


@bot.callback_query_handler(func=lambda call: call.data == 'show')
def show_your_acc(call):
    user = db.Users.find_one({'tg_id': call.message.chat.id})
    btns = types.InlineKeyboardMarkup(row_width=2)
    update_account = types.InlineKeyboardButton("Изменить анкету", callback_data='update')
    search_ = types.InlineKeyboardButton("Продолжить искать людей", callback_data='search')
    tests = types.InlineKeyboardButton("Пройти тесты", callback_data='show_tests')
    btns.add(update_account, search_, tests)
    bot.send_photo(
        call.message.chat.id,
        photo=open(user['img'], 'rb'),
        caption=generate_caption(user),
        reply_markup=btns
    )


@bot.callback_query_handler(func=lambda call: call.data == 'update')
def change_acc(call):
    update_acc(call.message)


def update_acc(message):
    btns = types.InlineKeyboardMarkup(row_width=2)
    name = types.InlineKeyboardButton('Имя', callback_data='update_name')
    age = types.InlineKeyboardButton('Возраст', callback_data='update_age')
    desc = types.InlineKeyboardButton('Описание', callback_data='update_desc')
    photo = types.InlineKeyboardButton('Фото', callback_data='update_photo')
    no_update = types.InlineKeyboardButton('Ничего', callback_data='show')
    btns.add(name, age, desc, photo, no_update)
    bot.send_message(message.chat.id, "Что ты хочешь изменить?", reply_markup=btns)


@bot.callback_query_handler(func=lambda call: call.data == 'update_name')
def change_name(call):
    bot.send_message(call.message.chat.id, "Введи новое имя")
    bot.register_next_step_handler(call.message, update_name, call.message.chat.id)


def update_name(message, tg_id):
    db.Users.update_one({'tg_id': tg_id}, {'$set': {'name': message.text}})
    bot.send_message(message.chat.id, "Ты сменил имя")
    update_acc(message)


@bot.callback_query_handler(func=lambda call: call.data == 'update_age')
def change_age(call):
    bot.send_message(call.message.chat.id, "Введи новый возраст")
    bot.register_next_step_handler(call.message, update_age, call.message.chat.id)


def update_age(message, tg_id):
    if type(message.text) == str:
        try:
            age = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, 'Впиши возраст цифрами, пожалуйста')
            bot.register_next_step_handler(message, update_age, tg_id)
        else:
            db.Users.update_one({'tg_id': tg_id}, {'$set': {'age': age}})
            bot.send_message(message.chat.id, 'Ты сменил свой возраст')
            update_acc(message)
    else:
        bot.send_message(message.chat.id, 'Впиши возраст цифрами, пожалуйста')
        bot.register_next_step_handler(message, update_age, tg_id)


@bot.callback_query_handler(func=lambda call: call.data == 'update_desc')
def change_desc(call):
    bot.send_message(call.message.chat.id, "Введи новое описание")
    bot.register_next_step_handler(call.message, update_desc, call.message.chat.id)


def update_desc(message, tg_id):
    db.Users.update_one({'tg_id': tg_id}, {'$set': {'description': message.text}})
    bot.send_message(message.chat.id, "Ты сменил описание")
    update_acc(message)


@bot.callback_query_handler(func=lambda call: call.data == 'update_photo')
def change_photo(call):
    bot.send_message(call.message.chat.id, "Отправь новое фото")
    bot.register_next_step_handler(call.message, update_photo, call.message.chat.id)


def update_photo(message, tg_id):
    if message.photo is None:
        bot.send_message(message.chat.id, 'Тебе нужно отправить фотграфию')
        bot.register_next_step_handler(message, update_photo, tg_id)
    else:
        path = save_photo(message.photo[-1], message.from_user.id)
        db.Users.update_one({'tg_id': tg_id}, {'$set': {'img': path}})
        bot.send_message(message.chat.id, "Ты сменил фото")
        update_acc(message)


@bot.callback_query_handler(func=lambda call: call.data == 'create')
def register(call):
    if is_in_base(db, call.message.chat.id):
        btns = types.InlineKeyboardMarkup(row_width=2)
        y = types.InlineKeyboardButton("Да", callback_data='update')
        n = types.InlineKeyboardButton("Нет", callback_data='nothing')
        btns.add(y, n)
        bot.send_message(call.message.chat.id, 'У тебя уже есть анкета. Хочешь ее отредактировать?', reply_markup=btns)
    else:
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
        bot.send_message(message.chat.id, 'Впиши возраст цифрами, пожалуйста')
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


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in ['search', 'like', 'dislike'])
def search(call):
    if call.data.split('_')[0] == 'like':
        from_ = call.message.chat.id
        prev = call.data.split('_')[1]
        prev = db.Users.find_one({'_id': ObjectId(prev)})
        to = prev['tg_id']
        db.Reactions.insert_one({'from': from_, 'to': to, 'isLike': True})
        if db.Reactions.find_one({'to': from_, 'from': to, 'isLike': True}):
            user = db.Users.find_one({'tg_id': from_})
            print('Match:', prev, user)
            match(prev, user)
    user = db.Users.find_one({'tg_id': call.message.chat.id})
    users = db.Users.find({'_id': {'$gte': user['last_searched']}}).sort('_id', ASCENDING)
    btns = types.InlineKeyboardMarkup(row_width=2)
    next_ = next(users, None)
    if next_:
        if next_['tg_id'] == call.message.chat.id:
            next_ = next(users, None)
        next_next = next(users, None)
        if next_next:
            db.Users.update_one({'tg_id': call.message.chat.id}, {'$set': {'last_searched': next_next['_id']}})
        else:
            db.Users.update_one({'tg_id': call.message.chat.id}, {'$set': {'last_searched': None}})
        if next_:
            like = types.InlineKeyboardButton("Нравится", callback_data=f'like_{next_["_id"]}')
            dislike = types.InlineKeyboardButton("Не нравится", callback_data='dislike')
            show_acc = types.InlineKeyboardButton("Вернуться к моей анкете", callback_data='show')
            btns.add(like, dislike, show_acc)
            bot.send_photo(
                call.message.chat.id,
                photo=open(next_['img'], 'rb'),
                caption=generate_caption(next_),
                reply_markup=btns
            )
        else:
            btns = types.InlineKeyboardMarkup() \
                .add(types.InlineKeyboardButton("Вернуться к моей анкете", callback_data='show'))
            bot.send_message(call.message.chat.id, "Анкеты закончились(", reply_markup=btns)
    else:
        btns = types.InlineKeyboardMarkup()\
            .add(types.InlineKeyboardButton("Вернуться к моей анкете", callback_data='show'))
        bot.send_message(call.message.chat.id, "Анкеты закончились(", reply_markup=btns)


def match(user1, user2):
    username1 = bot.get_chat_member(user1['tg_id'], user1['tg_id']).user.username
    username2 = bot.get_chat_member(user2['tg_id'], user2['tg_id']).user.username
    bot.send_photo(
        user1['tg_id'],
        photo=open(user2['img'], 'rb'),
        caption=generate_match(user2, username2),
    )
    bot.send_photo(
        user2['tg_id'],
        photo=open(user1['img'], 'rb'),
        caption=generate_match(user1, username1)
    )


def show_account(message, user):
    btns = types.InlineKeyboardMarkup(row_width=2)
    like = types.InlineKeyboardButton("Нравится", callback_data='like')
    dislike = types.InlineKeyboardButton("Не нравится", callback_data='dislike')
    show_acc = types.InlineKeyboardButton("Вернуться к моей анкете", callback_data='show')
    btns.add(like, dislike, show_acc)
    bot.send_photo(
        message.chat.id,
        photo=open(user['img'], 'rb'),
        caption=generate_caption(user),
        reply_markup=btns
    )


@bot.callback_query_handler(func=lambda call: call.data == 'show_tests')
def show_tests(call):
    tests = db.Tests.find()
    btns = types.InlineKeyboardMarkup(row_width=2)
    for test in tests:
        btn = types.InlineKeyboardButton(test["name"], callback_data=f'test_{test["name"]}_0_0')
        btns.add(btn)
    bot.send_message(call.message.chat.id, "Выбери тест", reply_markup=btns)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'test')
def testing(call):
    data = call.data.split('_')
    test_name = data[1]
    test = db.Tests.find_one({'name': test_name})
    score = int(data[2])
    question_n = int(data[3])
    question = test['questions'][question_n]
    print(question_n, len(test["questions"]))
    btns = types.InlineKeyboardMarkup(row_width=2)
    btns_ = []
    for i, answer in enumerate(question['answers']):
        if question_n == len(test["questions"]) - 1:
            cb_data = f'score_{test["name"]}_{score + answer["value"]}'
        else:
            cb_data = f'test_{test["name"]}_{score+int(answer["value"])}_{question_n+1}'
        btn = types.InlineKeyboardButton(
            i + 1,
            callback_data=cb_data
        )
        btns_.append(btn)
    btns.add(*btns_)
    n_ans = []
    c = 1
    for ans in question['answers']:
        n_ans.append((str(c), ans['name']))
        c += 1
    ans = '\n'.join(['. '.join(i) for i in n_ans])
    bot.send_message(
        call.message.chat.id,
        f"Вопрос {question_n+1}: {question['descriptions']}\n{ans}",
        reply_markup=btns
    )


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'score')
def calc_result(call):
    print('scored')
    data = call.data.split('_')
    test_name = data[1]
    test = db.Tests.find_one({'name': test_name})
    score = int(data[2])
    print(score)
    results = test['results']
    for res in results:
        res_n = list(res)
        if 'maxValue' not in res_n:
            f1 = True
        else:
            f1 = score < res['maxValue']
        if 'minValue' not in res_n:
            f2 = True
        else:
            f2 = score >= res['minValue']
        f = f1 and f2
        if f:
            btns = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Вернуться к анкете", callback_data='show')
            btns.add(btn)
            bot.send_message(
                call.message.chat.id,
                "Ваш результат:\n"+res["value"]+"\n\nУ нас есть беседа для таких как ты\n"+res["groupChatLink"],
                reply_markup=btns)
            db.Users.update_one({'tg_id': call.message.chat.id}, {'$set': {'testResult': res["value"]}})
            break
