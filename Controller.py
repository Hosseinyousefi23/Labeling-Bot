import pandas as pd
import numpy as np

from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging

class Controller():
    '''
    Description:    Every instances of this class will manage a specific user works.
                    this object is an intermediary between CmdAnalyzer and userDB
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        self.db_handler = None
        self.update = None
        self.state = 0
        self.request = None
        self.callback = False

 def new_message(self, message, callback=False):
        self.callback = callback # to remain that what was the last message
        if message == "/start":
            self.show_message("Welcoming :)")
            if self.check_user_permission():
                self.state = 0
                self.db_handler = None
                self.request = "gather_data"
                self.gather_data()
            else:
                self.show_message("Your telegram id is not allowed\nYou can ask @milad_mirzazadeh for access ")
        elif self.request == "gather_data":
            self.gather_data(message)
        elif self.db_handler == None:
            self.show_message("The Bot is not activated yet. \nYou can activate it by /start")

        else:
            if message == "/show_card":
                self.show_new_card(new_message=True)
            elif message == "show_translation":
                self.show_answer()
            elif message in ["correct_answer", "wrong_answer"]:
                self.check_answer(message)
            elif message == "/remaining":
                self.show_remaining_cards()
            else:
                self.show_message("Didn't understand")
