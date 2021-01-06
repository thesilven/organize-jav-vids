import re
import time
import json
import requests
import colorama
import cloudscraper
from bs4 import BeautifulSoup

# TODO: find chinese title source website


def getText(element):
    return element.getText()


class JAVInfoGetter:
    def __init__(self, setting, dataManager):
        self.setting = setting
        self.dataManager = dataManager

    def GetInfo(self, bangou, fileName):
        # TODO: move search database out of there
        info = self.dataManager.Search(bangou)
        if info:
            if info["title"]:
                print(f"Find success info of {bangou} in db")
                return info, True
            elif not self.setting.retryFailedDB:  # use failed info in db
                print(f"Find failed info of {bangou} in db")
                return info, False

        info = dict()
        link = self.GetWebContent(bangou)

        # print(self.soup.prettify())
        info["bangou"] = self.ParseBangou()
        info["title"] = self.ParseTitle(info["bangou"])
        info["tags"] = self.ParseTag()
        info["director"] = self.ParseDirector()
        info["maker"] = self.ParseMaker()
        info["actors"] = self.ParseActor()
        actors = info["actors"]
        if not actors or type(actors) is str and actors in ['----', 'N/A']:
            info['actors'] = 'Unknown'

        info["album"] = self.ParseAlbum()
        info["duration"] = self.ParseDuration()
        info["date"] = self.ParseDate()
        info["thumbs"] = self.ParseThumbs()
        info["rating"] = self.ParseRating()
        info["link"] = link

        if info["bangou"] and info["bangou"] != bangou:
            return None, False
        elif not info["title"]:
            info["bangou"] = bangou
            return info, False
        else:
            info["title"] = info["title"].replace(
                info["bangou"], "").strip(" ")

        self.dataManager.Add(info)
        # print(json.dumps(info, indent=4, ensure_ascii=False))

        if bangou != info["bangou"]:
            # info2 = info.copy()
            # info2["bangou"] = bangou
            # self.dataManager.Add(info2)
            return info, False
        # XXX: use timer instead sleep
        time.sleep(self.setting.getInfoInterval)

        return info, True


class JAVInfoGetter_javlibrary(JAVInfoGetter):
    def __init__(self, setting, dataManager):
        super().__init__(setting, dataManager)

    def GetWebContent(self, bangou):
        link = "http://www.javlibrary.com/" + self.setting.language + \
            "/vl_searchbyid.php?keyword=" + bangou
        response = requests.get(link)
        self.soup = BeautifulSoup(response.text, "html.parser")

        if self.soup.select_one(".videothumblist"):  # has multiple search result
            try:
                link = "http://www.javlibrary.com/" + self.setting.language + "/" + \
                    self.soup.select_one(".videothumblist").select_one(
                        ".video").select_one("a")["href"]
                response = requests.get(link)
                self.soup = BeautifulSoup(response.text, "html.parser")
            except:
                link = ""

        return link

    def ParseBangou(self):
        try:
            return self.soup.select_one("#video_id").select_one(".text").getText()
        except:
            return ""

    def ParseTitle(self, bangou):
        try:
            return self.soup.select_one(
                "#video_title").select_one("a").getText()
        except:
            return ""

    def ParseTag(self):
        try:
            return list(map(getText, self.soup.select_one("#video_genres").select("a")))
        except:
            return ""

    def ParseMaker(self):
        try:
            return self.soup.select_one("#video_maker").select_one("a").getText()
        except:
            return ""

    def ParseDirector(self):
        try:
            return self.soup.select_one("#video_director").select_one("a").getText()
        except:
            return ""

    def ParseActor(self):
        try:
            return list(map(getText, self.soup.select_one("#video_cast").select("a")))
        except:
            return ""

    def ParseAlbum(self):
        try:
            return "http:" + self.soup.select_one("#video_jacket").select_one("img").get("src")
        except:
            return ""

    def ParseDuration(self):
        try:
            return self.soup.select_one("#video_length").select_one(".text").getText()
        except:
            return ""

    def ParseDate(self):
        try:
            return self.soup.select_one("#video_date").select_one(".text").getText()
        except:
            return ""

    def ParseThumbs(self):  # FIXME: sometimes no thumb
        try:
            imgs = self.soup.select_one(".previewthumbs").select("img")
            imgs = imgs[1:]  # remove "../img/player.gif"
            imgs = [img["src"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRating(self):
        try:
            text = self.soup.select_one(
                "#video_review").select_one(".score").getText()
            rate = re.search("(\d+.*\d)", text).group(0)
            return str(float(rate))
        except:
            return ""


# TODO: now only support english version
class JAVInfoGetter_javdb(JAVInfoGetter):
    def __init__(self, setting, dataManager):
        super().__init__(setting, dataManager)

    def GetWebContent(self, bangou):  # XXX: improve
        link = "http://javdb.com/search?q=" + bangou
        response = requests.get(link)
        self.soup = BeautifulSoup(response.text, "html.parser")
        if not self.soup.select_one("#videos"):
            return ""
        try:  # TODO: check try range
            videos_a = self.soup.select_one("#videos").select('a')
            for video_a in videos_a:
                link = "http://javdb.com/" + video_a["href"] + "?locale=en"
                if self.setting.javdbToken:
                    cookies = {"remember_me_token": self.setting.javdbToken}
                else:
                    cookies = dict()
                response = requests.get(link, cookies=cookies)
                self.soup = BeautifulSoup(response.text, "html.parser")
                infos = self.soup.select_one(
                    ".video-panel-info").select(".panel-block")

                self.infoDict = dict()
                for info in infos:
                    key = info.select_one("strong")
                    if not key:
                        continue
                    key = key.getText().strip(":")
                    value = info.select_one("span").getText()
                    self.infoDict[key] = value

                if self.infoDict['ID'] and self.infoDict['ID'] == bangou:
                    return link
        except Exception as ex:
            # TODO: get web content failed
            print(ex)
            return link

        return link

    def ParseBangou(self):
        try:
            return self.infoDict["ID"]
        except:
            return ""

    def ParseTitle(self, bangou):
        try:
            return self.soup.select_one(".title").select_one("strong").getText()
        except:
            return ""

    def ParseTag(self):
        try:
            tags = self.infoDict["Tags"].split(",")
            tags = [tag.strip(u"\xa0").strip(" ") for tag in tags]
            return tags
        except:
            return ""

    def ParseMaker(self):
        try:
            return self.infoDict["Maker"]
        except:
            return ""

    def ParseDirector(self):
        try:
            return self.infoDict["Director"]
        except:
            return ""

    def ParseActor(self):
        try:
            return self.infoDict["Actor(s)"]
        except:
            return ""

    def ParseAlbum(self):
        try:
            return self.soup.select_one(".video-cover")["src"]
        except:
            return ""

    def ParseDuration(self):
        try:
            duration = self.infoDict["Duration"]
            duration = re.search("\d+", duration).group(0)
            return duration
        except:
            return ""

    def ParseDate(self):
        try:
            return self.infoDict["Date"]
        except:
            return ""

    def ParseThumbs(self):
        try:
            imgs = self.soup.select_one(".preview-images").select("a")
            imgs = [img["href"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRating(self):
        try:
            rating = self.infoDict["Rating"]
            rating = re.search("\d+.\d+", rating).group(0)
            return rating
        except:
            return ""

class JAVInfoGetter_r18(JAVInfoGetter):
    def __init__(self, setting, dataManager):
        super().__init__(setting, dataManager)

    def GetWebContent(self, bangou):  # XXX: improve
        link = "https://www.r18.com/common/search/searchword=" + bangou
        scraper = cloudscraper.CloudScraper()
        response = scraper.get(link)
        self.soup = BeautifulSoup(response.text, "html.parser")
        item_list = self.soup.select(".item-list")
        # print(item_list)
        if not item_list:
            return ""
        try:  # TODO: check try range
            for item in item_list:
                link = item.select_one('a')['href']
                # print(link)
                response = scraper.get(link)
                self.soup = BeautifulSoup(response.text, "html.parser")
                infos = self.soup.select_one(".product-details").dl
                print('infos', infos)
                # print('infos children', infos.children())

                self.infoDict = dict()
                key = ''
                value = ''
                for child in infos.children():
                    print(child)
                    if child.name == 'dt':
                        key = child.getText()
                    elif child.name == 'dd':
                        value = child.getText()

                    if key and value:
                        print(key, value)
                        self.infoDict[key.strip()] = value.strip()
                        key = ''
                        value = ''

                # if self.infoDict['ID'] and self.infoDict['ID'] == bangou:
                #     return link
        except Exception as ex:
            # TODO: get web content failed
            print(ex)
            return link

        return link

    def ParseBangou(self):
        try:
            return self.infoDict["ID"]
        except:
            return ""

    def ParseTitle(self, bangou):
        try:
            return self.soup.select_one(".title").select_one("strong").getText()
        except:
            return ""

    def ParseTag(self):
        try:
            tags = self.infoDict["Tags"].split(",")
            tags = [tag.strip(u"\xa0").strip(" ") for tag in tags]
            return tags
        except:
            return ""

    def ParseMaker(self):
        try:
            return self.infoDict["Maker"]
        except:
            return ""

    def ParseDirector(self):
        try:
            return self.infoDict["Director"]
        except:
            return ""

    def ParseActor(self):
        try:
            return self.infoDict["Actor(s)"]
        except:
            return ""

    def ParseAlbum(self):
        try:
            return self.soup.select_one(".video-cover")["src"]
        except:
            return ""

    def ParseDuration(self):
        try:
            duration = self.infoDict["Duration"]
            duration = re.search("\d+", duration).group(0)
            return duration
        except:
            return ""

    def ParseDate(self):
        try:
            return self.infoDict["Date"]
        except:
            return ""

    def ParseThumbs(self):
        try:
            imgs = self.soup.select_one(".preview-images").select("a")
            imgs = [img["href"] for img in imgs]
            return imgs
        except:
            return ""

    def ParseRating(self):
        try:
            rating = self.infoDict["Rating"]
            rating = re.search("\d+.\d+", rating).group(0)
            return rating
        except:
            return ""
