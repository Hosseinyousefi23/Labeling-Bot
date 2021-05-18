import numpy as np
import pandas as pd
class DBHAndler():
    # columns of main table = ad_id, label, labeler_telegram_id
    @staticmethod
    def prepare_new_ad(): # it should return an Ad instance
        return(Ad())

class Ad():
    list_of_tags = ["اقتصادی","آرایشی و بهداشتی","کودک","ورزشی"]
    def __init__(self, id=1):
        self.ad_id = id
        self.image_url = 'https://native.yektanet.com/static/media/upload/items/64433-250x165.jpg' # read from main table in dbhandler
        self.title = "Salllllllam"



class User():
    def __init__(self, tele_id):
        self.chat_id = None
        self.first_name = None # = first name + " " + last name ////// Sometimes people don't have username :)

        self.user_id = tele_id
        self.labeled_ad = dict()

    def label_ad(self, ad_obj, label):
        # TODO: add to main table in db

        # add to local ads dict
        self.labeled_ad[ad_obj] = label




