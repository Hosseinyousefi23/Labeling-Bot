import pandas as pd
import numpy as np
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import logging
from DBUpdater import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, JSON, Numeric, BigInteger
class Alchemy():
    objects_to_update_in_orm_db = list([])
    engine = create_engine('sqlite:///labeling_bot_objects.db', echo = True)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    @staticmethod
    def update_orm():

        with Alchemy.Session() as session:
            for obj in Alchemy.objects_to_update_in_orm_db:
                #################
                local_object = session.merge(obj)
                session.add(local_object)
                session.commit()
                #################

            Alchemy.objects_to_update_in_orm_db = []


from Model import *
from Model import User


class Controller(Alchemy.Base):

    ######################################################################### Adding class to ORM table
    __tablename__ = 'controllers'
    __table_args__ = {'extend_existing': True}
    user_id = Column(String, primary_key=True)
    #########################################################################

    # We use these to say thanks to users every 20 labels.
    show_poem_cycle = 10 # We will send gratitude after every Controller.gratitude_cycle ads labeled
    '''
    Description:    Every instances of this class will manage a specific user works.
                    this object is an intermediary between CmdAnalyzer and userDB
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        CommandAnalyzer.user_objects[self.user_id] = User(user_id)
        Alchemy.objects_to_update_in_orm_db.append(CommandAnalyzer.user_objects[self.user_id])
        self.current_ad = None #The ad that user is labelin at the current moment
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
            if message == "commit":
                self.commit()
            if message == "/show_leaderboard1234":
                self.show_leaderboard()
            if message == "/export_number_of_dones":
                self.export_number_of_dones()

            if message == "/show_descriptions":
                self.show_description()

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
        if len(CommandAnalyzer.user_objects[self.user_id].labeled_ad)% Controller.show_poem_cycle == Controller.show_poem_cycle-1:# Saying Thanks for participation
            self.show_message("یه بیت شعر زیبا برای تشکر و رفع خستگی ( این پیام هر {} تبلیغ یکبار فرستاده میشه) \n  ----------- \n {}".format(Controller.show_poem_cycle, CommandAnalyzer.user_objects[self.user_id].prepare_new_poem()))

    def export_number_of_dones(self):
        df = pd.DataFrame([], columns=["id","number_of_labels"])
        for obj in list(CommandAnalyzer.user_objects.values()):
            df = df.append({"id":obj.user_id, "number_of_labels":len(obj.labeled_ad)}, ignore_index=True)
        df.to_csv("number_of_labels.csv")


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
    def show_description(self):
        descriptions = ["✅ {}  :\n⬅ {}\n".format(Ad.tags_df.tag[i], Ad.tags_df.description[i]) for i in range(len(Ad.tags_df))]

        message = "\n".join(descriptions)
        self.show_message(message)

    def save_answer(self, list_of_labels):
        try:
            CommandAnalyzer.user_objects[self.user_id].label_ad(self.current_ad, list_of_labels)
        except:
            self.show_message("یکم گیج شدم :). لطفا با /show_ad ادامه بده.")

    def show_leaderboard(self):# Todo : find the most participating people and show them
        count_of_labels={}
        for i in list(CommandAnalyzer.user_objects.values()):
            count_of_labels[i.user_id] = len(i.labeled_ad)
        sort_orders = sorted(count_of_labels.items(), key=lambda x: x[1], reverse=True)
        message = ""
        for i in range(10):
            if i < len(sort_orders):
                if i == 0:
                    message+= "{}. {} 🏆\n".format(i+1, sort_orders[i][0])
                elif i == 1:
                    message += "{}. {} 🥈\n".format(i+1, sort_orders[i][0])
                elif i == 2:
                    message += "{}. {} 🥉\n".format(i+1, sort_orders[i][0])
                else:
                    message += "{}. {} \n".format(i+1, sort_orders[i][0])
            else:
                break
        self.show_message(message)


    def show_number_of_done(self):
        number_of_done = len(CommandAnalyzer.user_objects[self.user_id].labeled_ad)
        self.show_message("تعداد تبلیغ تگ زده شده: {} \n برای ادامه میتونی از /show_ad  استفاده کنی :)".format(number_of_done))

class CommandAnalyzer():
    user_objects = {}
    user_chatid = {}
    if Alchemy.engine.dialect.has_table(Alchemy.engine.connect(), "users"):
        objects = Alchemy.session.query(User).all()
        for obj in objects:
            user_objects[obj.user_id] = obj
            user_chatid[obj.user_id] = obj.chat_id

    user_controller_objects = {}
    if Alchemy.engine.dialect.has_table(Alchemy.engine.connect(), "controllers"):
        objects = Alchemy.session.query(Controller).all()
        for obj in objects:
            user_controller_objects[obj.user_id] = obj


    bot = Bot("1515031822:AAFj9Z8AFJeXar0UuSmdaKp9Nn22nGY6AjY")

    def handle_new_callback(update, context):
        CommandAnalyzer.handle_new_message(update, context, callback=True)

    def handle_new_message(update, context, callback=False):
        if callback:
            user_id = update.callback_query.from_user.username
            if user_id == None :
                user_id = str(update.callback_query.from_user.first_name) + "//" + str(update.callback_query.from_user.last_name)  # This is for the ones who don't have telegram username
        else:
            try:
                user_id = update.message.from_user.username
                if user_id == None :
                    user_id = str(update.message.from_user.first_name) + "//" + str(update.message.from_user.last_name)  # This is for the ones who don't have telegram username
            except:
                pass
        if user_id not in CommandAnalyzer.user_chatid: # Creating a Controller instance
            if not callback:
                CommandAnalyzer.user_chatid[user_id] = update.message.chat_id
            else:
                CommandAnalyzer.user_chatid[user_id] = update.callback_query.message.chat_id

            CommandAnalyzer.user_controller_objects[user_id] = Controller(user_id)
            CommandAnalyzer.user_objects[user_id].chat_id = CommandAnalyzer.user_chatid[user_id]
            Alchemy.objects_to_update_in_orm_db.append(CommandAnalyzer.user_controller_objects[user_id])







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




    def edit_message_text(user_id, message="hello",photo_url=None, reply_markup=None):
        try:
            if CommandAnalyzer.user_controller_objects[user_id].callback:
                CommandAnalyzer.user_controller_objects[user_id].update.callback_query.edit_message_text(message, reply_markup=reply_markup)
            else:
                CommandAnalyzer.user_controller_objects[user_id].update.message.edit_text(message, reply_markup=reply_markup)

        except:
            CommandAnalyzer.user_controller_objects[user_id].show_message("بنظر میرسه که یه چیزی رو اشتباه وارد کردی :(")




Alchemy.Base.metadata.create_all(Alchemy.engine)