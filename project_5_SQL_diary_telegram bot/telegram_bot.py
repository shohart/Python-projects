import telebot

bot = telebot.TeleBot("")


@bot.message_handler(commands=["start", "stop"])
def start(message):
    bot.send_message(message.chat.id, "Hello!")


bot.polling()
