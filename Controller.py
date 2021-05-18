import pandas as pd
import numpy as np

from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging

# from CommandAnalyzer import *
from Model import *


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
                user_id = str(update.callback_query.from_user.first_name) + "//" + str(update.callback_query.from_user.last_name)  # This is for the ones who don't have telegram username
        else:
            user_id = update.message.from_user.username
            if user_id == None :
                user_id = str(update.message.from_user.first_name) + "//" + str(update.message.from_user.last_name)  # This is for the ones who don't have telegram username

        if user_id not in CommandAnalyzer.user_chatid: # Creating a Controller instance
            print('hellllllllllllo')
            CommandAnalyzer.user_chatid[user_id] = update.message.chat_id
            CommandAnalyzer.user_controller_objects[user_id] = Controller(user_id)

        if callback:
            message = update.callback_query.data
        else:
            message = update.message.text
        CommandAnalyzer.user_controller_objects[user_id].update = update
        print(CommandAnalyzer.user_chatid)
        CommandAnalyzer.user_controller_objects[user_id].new_message(message, callback)





    def show_to_user(user_id, text, photo_url=None, reply_markup = None):
        if photo_url == None :
            CommandAnalyzer.bot.send_message(chat_id=CommandAnalyzer.user_chatid[user_id], text=text, reply_markup=reply_markup)
        if photo_url != None :
            CommandAnalyzer.bot.send_photo(chat_id= CommandAnalyzer.user_chatid[user_id], photo=photo_url, caption=text)





    def edit_message_text(user_id, message="hello",photo_url=None, reply_markup=None): #TODO: revise this shit
        try:
            if CommandAnalyzer.user_controller_objects[user_id].callback:
                CommandAnalyzer.user_controller_objects[user_id].update.callback_query.edit_message_text(message, reply_markup=reply_markup)
            else:
                CommandAnalyzer.user_controller_objects[user_id].update.message.edit_text(message, reply_markup=reply_markup)

        except:
            CommandAnalyzer.user_controller_objects[user_id].show_message("بنظر میرسه که یه چیزی رو اشتباه وارد کردی :(")


class Controller():
    '''
    Description:    Every instances of this class will manage a specific user works.
                    this object is an intermediary between CmdAnalyzer and userDB
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_obj = User(user_id)# TODO : Create a User instance
        self.current_ad = None #The add that user is labelin at the current moment
        self.update = None
        self.state = 0
        self.request = None
        self.callback = False

    def new_message(self, message, callback=False):
        self.callback = callback # to remain that what was the last message
        if message == "/start":
            self.show_message("Welcoming :)")
            self.welcome_to_user()
        else:
            if message == "/show_ad":
                self.show_new_ad()
            if message == "show_tags":
                self.show_tags()
            elif message in Ad.list_of_tags:
                self.save_answer(message)
                self.show_new_ad()
            elif message == "/number_of_done":
                self.show_number_of_done()
            else:
                pass

    def show_message(self, message,photo_url=None, reply_markup=None, edit=False):
        if not edit:
            CommandAnalyzer.show_to_user(self.user_id, message, photo_url=photo_url, reply_markup=reply_markup)
        else:
            CommandAnalyzer.edit_message_text(self.user_id, message, photo_url=photo_url, reply_markup=reply_markup)

    def welcome_to_user(self):
        self.show_message("سلام  خیلی خوش اومدی و ممنونیم از کمکت. \n برای شروع میتونی از دستور /show_ad استفاده کنی 😍")

    def show_new_ad(self):
         # TODO : get new ad from db handler -> Create new Ad instance -> Show to user : img and caption with a markup
        self.current_ad = DBHAndler.prepare_new_ad()
        self.show_message(message = self.current_ad.title, photo_url=self.current_ad.image_url)
        # Here we are creating a button for showing tags
        keyboard = [[InlineKeyboardButton("🏷🏷🏷 نمایش دسته بندی ها", callback_data='show_tags')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.show_message(message="برای انتخاب موضوع، دکمه زیر رو بزن", reply_markup=reply_markup, edit=False)

    def show_tags(self):
        keyboard = [[InlineKeyboardButton(tag, callback_data=tag)] for tag in Ad.list_of_tags]
        reply_markup = InlineKeyboardMarkup(keyboard)
        answer = "موضوع مناسب رو انتخاب کن"
        self.show_message(answer, reply_markup= reply_markup, edit=True)

    def save_answer(self, label):
        self.user_obj.labeled_ad(self.current_ad, label)


    def show_number_of_done(self):
        number_of_done = len(self.user_obj.labeled_ad)
        self.show_message("تعداد تبلیغ تگ زده شده: {} \n برای ادامه میتونی از /show_ad  استفاده کنی :)".format(number_of_done))





