import requests

class DangDangUtils:
    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.token = token

    def __get(self, PARAMS):
        PARAMS["token"] = self.token
        PARAMS["deviceType"] = "Android"
        result = requests.get(url=self.endpoint, params=PARAMS)
        return result.json()

    def daily_sign_in(self):
        return self.__get({'action': 'signin'})

    def get_cloud_bookshelf_list(self):
        return self.__get({'action': 'getCloudBookShelfList'})["mediaList"]

    def get_book_info(self, productId):
        PARAMS = {'action': 'getMedia'}
        PARAMS["mediaId"] = productId
        return self.__get(PARAMS)["data"]

    def get_book_cloud_sync_read_info(self, productId):
        PARAMS = {'action': 'getBookCloudSyncReadInfo', 'versionTime': '0'}
        PARAMS["productId"] = productId
        return self.__get(PARAMS)

    def get_book_cloud_sync_read_progress_info(self, productId):
        PARAMS = {'action': 'getBookCloudSyncReadProgressInfo'}
        PARAMS["productId"] = productId
        return self.__get(PARAMS)["data"]
