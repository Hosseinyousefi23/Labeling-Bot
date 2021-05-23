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
            if not callback:
                CommandAnalyzer.user_chatid[user_id] = update.message.chat_id
            else:
                CommandAnalyzer.user_chatid[user_id] = update.callback_query.message.chat_id
            CommandAnalyzer.user_controller_objects[user_id] = Controller(user_id)


        if callback:
            message = update.callback_query.data
        else:
            message = update.message.text
        CommandAnalyzer.user_controller_objects[user_id].update = update
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

    # We use these to say thanks to users every 20 labels.
    Gratitudes = ["زحمتی که می‌کشی خیلی برامون ارزشمنده. ممنون ❤️","خسته نباشی 😇","تشکر فراوان بابت وقتی که داری میذاری ☺️",
                  "خیر از جوونی‌ت ببینی 😌","ماشالا پهلوان :))","هر یه دونه تگی که میزنی دقت الگوریتم‌های ما رو بالاتر میبره. مرسی 🥰",
                  "سیاهی لشکر نیاید به کار  *** یکی مرد جنگی به از صدهزار \nاینم یه بیت شعر جهت رفع خستگی شما 😄","شعر جهت رفع خستگی : \nگفتند یافت می‌نشود جسته‌ایم ما \nگفت آن که یافت می‌نشود آنم آرزوست😏 \n",
                  "شعر خوب برای آدم خوب💐:))\nهر که را می‌بینم از کار جهان در محنت است\nکار ما داریم کز کار جهان آسوده‌ایم",
                  "این شعر برای در رفتن خستگیه :)👇\nنخش هر قدر طولانی، همان اندازه تنها تر \nکسی دلتنگی یک بادبادک را نمی‌فهمد 🪁"]
    gratitude_cycle = 7 # We will send gratitude after every Controller.gratitude_cycle ads labeled
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
        self.current_selected_tags = [] # we print green check emoji next to the selected tags. For this we have to save which tags are selected by the user for the current ad//// we use this var in show_tags_method

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
            if message == "/show_leaderboard1234":
                #TODO : return most participating people
                pass
            elif message in Ad.list_of_tags:
                if message in self.current_selected_tags:
                    self.current_selected_tags.remove(message)
                else:
                    self.current_selected_tags.append(message)
                self.show_tags()
            elif message == "go_to_next_ad":
                if len(self.current_selected_tags) == 0:
                    self.show_message("حداقل باید یک تگ رو انتخاب کنی، اگه هیچکدوم مناسب نبود، گزینه‌ی هیچکدام رو انتخاب کن 🤓 ")
                    return(0)
                else:
                    self.save_answer(self.current_selected_tags)
                    selected_tags_in_str = "🔹".join(self.current_selected_tags)
                    self.show_message("تگ انتخاب شده برای تبلیغ بالا👆 :   🔹{}🔹".format(selected_tags_in_str),edit = True)
                    self.show_new_ad()
            elif message == "/number_of_done":
                self.show_number_of_done()
            else:
                pass

    def show_message(self, message,photo_url=None, reply_markup=None, edit=False):
        try:
            if not edit:
                CommandAnalyzer.show_to_user(self.user_id, message, photo_url=photo_url, reply_markup=reply_markup)
            else:
                CommandAnalyzer.edit_message_text(self.user_id, message, photo_url=photo_url, reply_markup=reply_markup)
        except:
            CommandAnalyzer.show_to_user(self.user_id, "به نظر میرسه یه چیزی رو اشتباه وارد کردی. با دستور /show_ad میتونی ادامه بدی ^^", photo_url=photo_url, reply_markup=reply_markup)

    def welcome_to_user(self):
        self.show_message("سلام  خیلی خوش اومدی و ممنونیم از کمکت. \n برای شروع میتونی از دستور /show_ad استفاده کنی 😍")

    def show_new_ad(self):
        self.current_selected_tags = []
        self.current_ad = DBHandler.prepare_new_ad()
        self.show_message(message = "عنوان تبلیغ : {}".format(self.current_ad.title), photo_url=self.current_ad.image_url)
        # Here we are creating a button for showing tags
        keyboard = [[InlineKeyboardButton("🏷🏷🏷 نمایش دسته بندی ها", callback_data='show_tags')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.show_message(message="برای انتخاب موضوعات، دکمه زیر رو بزن 😎", reply_markup=reply_markup, edit=False)
        if len(self.user_obj.labeled_ad)% Controller.gratitude_cycle == Controller.gratitude_cycle-1:# Saying Thanks for participation
            self.show_message(np.random.choice(Controller.Gratitudes))

    def show_tags(self):
        keyboard = list([])
        tags_list = list([])
        for tag in Ad.list_of_tags:  # Here we are creating a new list of tags to add green_tik_emojies next to selected tags, But Callbacks are still from Ad.list_of_tags
            if tag in self.current_selected_tags:
                tags_list.append("✅ {}".format(tag))
            else:
                tags_list.append(tag)

        for tag_num in np.arange(0, len(tags_list), step=2):
            if tag_num == len(tags_list)-1 :
                keyboard.append([InlineKeyboardButton(tags_list[tag_num], callback_data=Ad.list_of_tags[tag_num])])
                break
            keyboard.append([InlineKeyboardButton(tags_list[tag_num], callback_data=Ad.list_of_tags[tag_num]),
                         InlineKeyboardButton(tags_list[tag_num+1], callback_data=Ad.list_of_tags[tag_num+1])])
        keyboard.append([InlineKeyboardButton("تمومه! بریم بعدی", callback_data="go_to_next_ad")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        answer = "موضوعات مرتبط رو انتخاب کن"
        self.show_message(answer, reply_markup= reply_markup, edit=True)

    def save_answer(self, list_of_labels):
        try:
            self.user_obj.label_ad(self.current_ad, list_of_labels)
        except:
            self.show_message("یکم گیج شدم :). لطفا با /show_ad ادامه بده.")



    def show_number_of_done(self):
        number_of_done = len(self.user_obj.labeled_ad)
        self.show_message("تعداد تبلیغ تگ زده شده: {} \n برای ادامه میتونی از /show_ad  استفاده کنی :)".format(number_of_done))





