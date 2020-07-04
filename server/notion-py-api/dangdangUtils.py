import requests

class DangDangUtils(object):
    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.token = token

    def __get(self, PARAMS):
        PARAMS["token"] = self.token
        PARAMS["deviceType"] = "Android"
        r = requests.get(url=self.endpoint, params=PARAMS)
        return r.json()

    def dailySignIn(self):
        return self.__get({'action': 'signin'})

    def getCloudBookShelfList(self):
        return self.__get({'action': 'getCloudBookShelfList'})["mediaList"]

    def getBookInfo(self, productId):
        PARAMS = {'action': 'getMedia'}
        PARAMS["mediaId"] = productId
        return self.__get(PARAMS)["data"]

    def getBookCloudSyncReadInfo(self, productId):
        PARAMS = {'action': 'getBookCloudSyncReadInfo', 'versionTime': '0'}
        PARAMS["productId"] = productId
        return self.__get(PARAMS)

    # ????
    def getBookCloudSyncReadProgressInfo(self, productId):
        PARAMS = {'action': 'getBookCloudSyncReadProgressInfo'}
        PARAMS["productId"] = productId
        return self.__get(PARAMS)["data"]
