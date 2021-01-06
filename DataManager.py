import json
from pathlib import Path
from pymongo import MongoClient
# import bson
# from bson import json_util
# import pymongo


class DataManager:
    def __init__(self, setting):
        self.setting = setting
        self.mongo_client = MongoClient(self.setting.mongoDbUrl)

        # self.dbpath = Path("db-" + self.setting.language + ".json")

        # if not self.dbpath.exists():
        #     self.dbpath.touch()
        #     self.dbdata = {}
        # else:
        #     with open(self.dbpath) as self.dbfile:
        #         dbtext = self.dbfile.read()
        #         if not dbtext:
        #             self.dbdata = {}
        #         else:
        #             self.dbdata = json.loads(dbtext)

        # print("read db")
        # print(self.dbdata)

    def Add(self, info):
        # self.dbdata.update({info["bangou"]: info})
        db = self.mongo_client.jav
        if info and info['bangou']:
            info_from_db = db.jav_data.find_one({'bangou': info['bangou']})
            if not info_from_db:
                result = db.jav_data.insert_one(info)
                # info.pop('_id', None)

    def Save(self):
        # print("save db")
        # with open(self.dbpath, "w") as self.dbfile:
        #     json.dump(self.dbdata, self.dbfile)
        #     self.dbfile.close()
        pass

    def Search(self, bangou):
        # if bangou in self.dbdata:
        #     return self.dbdata[bangou]
        # else:
        #     return None
        db = self.mongo_client.jav
        info_from_db = db.jav_data.find_one({'bangou': bangou})
        if info_from_db:
            return info_from_db
        else:
            return None
