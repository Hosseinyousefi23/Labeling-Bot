from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Bot,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging

from Controller import *


class CommandAnalyzer():
    user_objects = {}
    user_chatid = {}
    user_controller_objects = {}
    bot = Bot("1515031822:AAFj9Z8AFJeXar0UuSmdaKp9Nn22nGY6AjY")


    def handle_new_callback(update, context):
        CommandAnalyzer.handle_new_message(update, context, callback=True)

    def handle_new_message(update, context, callback=False):
        if callback:
            user_id = update.callback_query.from_user.username
            if user_id == None :
                user_id = update.callback_query.from_user.first_name + "//" + update.callback_query.from_user.last_name  # This is for the ones who don't have telegram username
        else:
            user_id = update.message.from_user.username
            if user_id == None :
                user_id = update.message.from_user.first_name + "//" + update.message.from_user.last_name  # This is for the ones who don't have telegram username

        if user_id not in CommandAnalyzer.user_chatid: # Creating a Controller instance
            CommandAnalyzer.user_chatid[user_id] = update.message.chat_id
            CommandAnalyzer.user_controller_objects[user_id] = Controller(user_id)

        if callback:
            message = update.callback_query.data
        else:
            message = update.message.text
        CommandAnalyzer.user_controller_objects[user_id].update = update
        CommandAnalyzer.user_controller_objects[user_id].new_message(message, callback)




    def show_to_user(user_id, text, photo_url=None, reply_markup = None):
        CommandAnalyzer.bot.send_message(chat_id=CommandAnalyzer.user_chatid[user_id], text=text, reply_markup=reply_markup)
        if photo_url != None :
            CommandAnalyzer.bot.send_photo(chat_id= CommandAnalyzer.user_chatId[user_id], photo_url, text)





    def edit_message_text(user_id, message="hello", reply_markup=None): #TODO: revise this shit
        try:
            if CommandAnalyzer.user_controller_objects[user_id].callback:
                CommandAnalyzer.user_controller_objects[user_id].update.callback_query.edit_message_text(message, reply_markup=reply_markup)
            else:
                CommandAnalyzer.user_controller_objects[user_id].update.message.edit_text(message, reply_markup=reply_markup)

        except:
            CommandAnalyzer.user_controller_objects[user_id].show_message("بنظر میرسه که یه چیزی رو اشتباه وارد کردی :(")