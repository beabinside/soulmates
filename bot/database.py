from pymongo import MongoClient


def connect_to_db(url):
    client = MongoClient(url)
    db = client.Testerpsychobot
    return db


def is_in_base(db, tg_id):
    return db.Users.find_one({'tg_id': tg_id}) is not None


def add_user_to_base(db, user):
    db.Users.insert_one(user)
    print(user)
