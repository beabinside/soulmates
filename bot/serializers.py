def create_user():
    return {
        'name': '',
        'description': '',
        'age': 0,
        'img': '',
        'testResult': '',
        'tg_id': ''
    }


def generate_caption(user):
    return f'{user["name"]}, {user["age"]}\n{user["description"]}'
