import numpy as np
import pandas as pd
import os.path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from Controller import *
from sqlalchemy import Column, Integer, String, JSON, BigInteger
import logging

class Ad(Alchemy.Base):

    tags_df = pd.read_csv("tags.csv")
    list_of_tags_without_nothing = list(tags_df.tag.unique())
    list_of_tags = list_of_tags_without_nothing + ["هیچکدام",]

    ######################################################################### Adding class to ORM table
    __tablename__ = 'ads'
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    image_url = Column(String)
    title = Column(String)
    advertiser_id = Column(Integer)
    #########################################################################

    def __init__(self, id, title, image, campain_id, advertiser_id):
        self.id = int(id)
        self.image_url = image # read from main table in dbhandler
        self.title = title
        self.advertiser_id = int(advertiser_id)
        self.campain_id = int(campain_id)

class DBHandler():
    '''
    We will save the local data to the output csv file every 100 labels added. Then we're gonna read next 100 rows and save as local table
    '''
    # columns of main table (which will be written in the output_file.csv) = ad_id, label, labeler_userid (user id is either tele_id or firstame//lastname) , advertiser_id, campaing_id
    size_of_batch = 30 # how many ads we collect from data file and use as local. Default : 100
    ad_data_file_path = "items.csv"
    local_result_table = pd.DataFrame([], columns=["ad_id", "labels", "labeler_userid", "advertiser_id", "campaign_id"])
    result_file_path = 'result.csv'
    result_file = pd.DataFrame([])
    local_table = pd.DataFrame([])
    local_table_pointer = 0 # pointer is a row number in the data_file

    if os.path.isfile(result_file_path):
        input_file_table_pointer = len(pd.read_csv(result_file_path))
    else:
        input_file_table_pointer = 0 # pointer is a row number in the data_file
    there_is_no_more_data = False


    @staticmethod
    def prepare_new_ad(): # it should return an Ad instance
        if len(DBHandler.local_table)==0:
            DBHandler.fetch_new_batch()
        if DBHandler.local_table_pointer >= DBHandler.size_of_batch:
            DBHandler.fetch_new_batch()
            DBHandler.local_table_pointer=0
        row = DBHandler.local_table.iloc[DBHandler.local_table_pointer]
        DBHandler.local_table_pointer += 1
        # logging.info("local table pointer = {}, ") # TODO : log which ad is being showed to wich person. which row are we in input db
        new_ad_obj = Ad(row.id, row.title, row.image, row.campaign_id, row.advertiser_id)
        Alchemy.objects_to_update_in_orm_db.append(new_ad_obj)

        return(new_ad_obj)

    @staticmethod
    def fetch_new_batch():
        Alchemy.update_orm()
        if DBHandler.there_is_no_more_data:
            DBHandler.end_of_database()
            return(0)
        all_items = pd.read_csv(DBHandler.ad_data_file_path, index_col=0)
        DBHandler.local_table = all_items.iloc[DBHandler.input_file_table_pointer: DBHandler.input_file_table_pointer+DBHandler.size_of_batch]
        if len(DBHandler.local_table) <DBHandler.size_of_batch :
            DBHandler.there_is_no_more_data = True
        DBHandler.input_file_table_pointer += DBHandler.size_of_batch
        DBHandler.local_table_pointer = 0
    @staticmethod
    def add_to_local_result(ad:Ad, labels, user_id):
        DBHandler.local_result_table =DBHandler.local_result_table.append({"ad_id": ad.id, "labels": labels, "labeler_userid":user_id,
                                             "advertiser_id": ad.advertiser_id, "campaign_id":ad.campain_id}, ignore_index=True)
        if len(DBHandler.local_result_table) >= DBHandler.size_of_batch:
            DBHandler.write_local_result_to_database()

    @staticmethod
    def write_local_result_to_database():
        try:
            DBHandler.result_file = pd.read_csv(DBHandler.result_file_path, index_col=0)
        except:
            pass
        DBHandler.result_file = DBHandler.result_file.append(DBHandler.local_result_table)
        DBHandler.local_result_table = pd.DataFrame([],columns=["ad_id", "labels", "labeler_userid", "advertiser_id", "campaign_id"])
        DBHandler.result_file.to_csv(DBHandler.result_file_path)


    @staticmethod
    def end_of_database():
        print("finished")







class User(Alchemy.Base):
    ######################################################################### Adding class to ORM table
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_id = Column(String, primary_key=True)
    chat_id = Column(BigInteger)
    labeled_ad = Column(JSON)
    #########################################################################

    def __init__(self, tele_id):
        self.all_poems = list(pd.read_csv('poems.csv', header=None).iloc[:,0])
        self.remaining_poems= self.all_poems
        self.chat_id = None
        self.user_id = tele_id
        self.labeled_ad = dict()

    def label_ad(self, ad_obj, labels):
        Alchemy.objects_to_update_in_orm_db.append(self)
        DBHandler.add_to_local_result(ad_obj, labels, self.user_id)
        # add to local ads dict
        self.labeled_ad[str(ad_obj.id)] = labels
    def prepare_new_poem(self):
        if len(self.remaining_poems==0):
            self.remaining_poems = self.all_poems
        poem = self.remaining_poems[0]
        self.remaining_poems.remove(self.remaining_poems[0])
        return(poem)






