import numpy as np
import pandas as pd
class DBHAndler():
    # columns of main table = ad_id, label, labeler_telegram_id
    pass
class Ad():
    def __init__(self, id):
        self.ad_id = id
        self.image_url = _ # read from main table in dbhandler


class User():
    def __init__(self, tele_id):
        self.chat_id = _
        self.name = _ # = first name + " " + last name ////// Sometimes people don't have username :)
        self.user_id = tele_id
        self.labeled_ad = dict()

    def label_ad(self, ad_obj, label):
        # TODO: add to main table in db

        # add to self ads dict
        self.labeled_ad[ad_obj] = label




