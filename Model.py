import numpy as np
import pandas as pd

class Ad():
    tags_df = pd.read_csv("tags.csv")
    list_of_tags = list(tags_df.subcat.unique())
    del list_of_tags[-3:-1]

    def __init__(self, id, title, image, campain_id, advertiser_id):
        self.id = id
        self.image_url = image # read from main table in dbhandler
        self.title = title
        self.advertiser_id = advertiser_id
        self.campain_id = campain_id

class DBHandler():
    '''
    We will save the local data to the output csv file every 100 labels added. Then we're gonna read next 100 rows and save as local table
    '''
    # columns of main table (which will be written in the output_file.csv) = ad_id, label, labeler_userid (user id is either tele_id or firstame//lastname) , advertiser_id, campaing_id
    size_of_batch = 20 # how many ads we collect from data file and use as local. Default : 100
    ad_data_file_path = "item2.csv"
    local_result_table = pd.DataFrame([], columns=["ad_id", "label", "labeler_userid", "advertiser_id", "campaign_id"])
    result_file_path = 'result.csv'
    result_file = pd.DataFrame([])
    local_table = pd.DataFrame([])
    local_table_pointer = 0 # pointer is a row number in the data_file
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
        return(Ad(row.id, row.title, row.image, row.campaign_id, row.advertiser_id))

    @staticmethod
    def fetch_new_batch():
        if DBHandler.there_is_no_more_data:
            DBHandler.end_of_database()
            return(0)
        all_items = pd.read_csv(DBHandler.ad_data_file_path)
        DBHandler.local_table = all_items.iloc[DBHandler.input_file_table_pointer: DBHandler.input_file_table_pointer+DBHandler.size_of_batch]
        if len(DBHandler.local_table) <DBHandler.size_of_batch :
            DBHandler.there_is_no_more_data = True
        DBHandler.input_file_table_pointer += DBHandler.size_of_batch
        DBHandler.local_table_pointer = 0
    @staticmethod
    def add_to_local_result(ad:Ad, label, user_id):
        DBHandler.local_result_table =DBHandler.local_result_table.append({"ad_id": ad.id, "label": label, "labeler_userid":user_id,
                                             "advertiser_id": ad.advertiser_id, "campaign_id":ad.campain_id}, ignore_index=True)
        if len(DBHandler.local_result_table) >= DBHandler.size_of_batch:
            DBHandler.write_local_result_to_database()

    @staticmethod
    def write_local_result_to_database():
        try:

            DBHandler.result_file = pd.read_csv(DBHandler.result_file_path)
        except:
            pass
        DBHandler.result_file = DBHandler.result_file.append(DBHandler.local_result_table)
        DBHandler.local_result_table = pd.DataFrame([],columns=["ad_id", "label", "labeler_userid", "advertiser_id", "campaign_id"])
        DBHandler.result_file.to_csv(DBHandler.result_file_path)


    @staticmethod
    def end_of_database():
        pass





class User():
    def __init__(self, tele_id):
        self.chat_id = None
        self.first_name = None # = first name + " " + last name ////// Sometimes people don't have username :)
        self.user_id = tele_id
        self.labeled_ad = dict()

    def label_ad(self, ad_obj, label):
        # TODO: add to main table in db
        DBHandler.add_to_local_result(ad_obj, label, self.user_id)
        # add to local ads dict
        self.labeled_ad[ad_obj] = label




