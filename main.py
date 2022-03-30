from bot.soulmate_bot import sm_bot


def main():
    sm_bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
