import pandas as pd
import numpy as np
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Bot,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging


def handle_new_message(update, context):
    new_message=message = update.message.text
    bot = Bot("1515031822:AAFj9Z8AFJeXar0UuSmdaKp9Nn22nGY6AjY")
    print(update.message.from_user.username)



    bot.send_photo(update.message.chat_id, 'https://native.yektanet.com/static/media/upload/items/64433-250x165.jpg')




def main():

    updater = Updater("1515031822:AAFj9Z8AFJeXar0UuSmdaKp9Nn22nGY6AjY", use_context=True)
    # CommandAnalyzer.bot = Bot("1515031822:AAFj9Z8AFJeXar0UuSmdaKp9Nn22nGY6AjY")

    dp = updater.dispatcher


    dp.add_handler(CommandHandler(["start", "main_menu"], handle_new_message))
    # dp.add_handler(CallbackQueryHandler(CommandAnalyzer.handle_new_callback, pattern=None))

    # dp.add_handler(MessageHandler(Filters.text, CommandAnalyzer.handle_new_message))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()