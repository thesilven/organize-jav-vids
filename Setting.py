import json


class Setting:
    def __init__(self):
        with open("config.json") as configFile:
            settingJson = json.load(configFile)

        try:
            self.fileExts = settingJson["fileExts"]
            self.fileExtsOnly = settingJson["fileExtsOnly"]
            self.fileDir = settingJson["fileDir"]
            self.destDir = settingJson["destDir"]
            self.getInfoInterval = settingJson["getInfoInterval"]
            self.fileNameFormat = settingJson["fileNameFormat"]
            self.language = settingJson["language"]
            self.saveAlbum = settingJson["saveAlbum"]
            self.dryRun = settingJson["dryRun"]
            self.maxFileLength = settingJson["maxFileLength"]
            self.minFileSizeMB = settingJson["minFileSizeMB"]
            self.renameCheck = settingJson["renameCheck"]
            self.saveThumb = settingJson["saveThumb"]
            self.ignoreWords = settingJson["ignoreWords"]
            self.retryFailedDB = settingJson["retryFailedDB"]
            self.javdbToken = settingJson["javdbToken"]
            self.mongoDbUrl = settingJson["mongoDbUrl"]
            # TODO: enable db or not
        except:
            print("read config file failed")
            exit(1)
