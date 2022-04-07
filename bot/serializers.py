def create_user():
    return {
        'name': '',
        'description': '',
        'age': 0,
        'img': '',
        'testResult': '',
        'tg_id': '',
        'last_searched': ''
    }


def generate_caption(user):
    return f'{user["name"]}, {user["age"]}\n{user["description"]}'


def generate_match(user, username):
    return f'Совпадение!\n{generate_caption(user)}\n\ntg: @{username}'
