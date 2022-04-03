from bot.soulmate_bot import bot


def main():
    print("Bot started")
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
