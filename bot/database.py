from pymongo import MongoClient, ASCENDING


def connect_to_db(url):
    client = MongoClient(url)
    db = client.Testerpsychobot
    return db


def is_in_base(db, tg_id):
    return db.Users.find_one({'tg_id': tg_id}) is not None


def add_user_to_base(db, user):
    user['last_searched'] = db.Users.find().sort('_id', ASCENDING)[2]['_id']
    db.Users.insert_one(user)
    user = db.Users.find_one({'tg_id': user['tg_id']})
    db.Users.update_many({'last_searched': None}, {'$set': {'last_searched': user['_id']}})
    print('New user:', user)
