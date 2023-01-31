import telebot

bot = telebot.TeleBot("5328965499:AAF4FVDiftcg-PUfODuJ8sDOsoSCKmISh0w")


@bot.message_handler(commands=["start", "stop"])
def start(message):
    bot.send_message(message.chat.id, "Hello!")


bot.polling()
