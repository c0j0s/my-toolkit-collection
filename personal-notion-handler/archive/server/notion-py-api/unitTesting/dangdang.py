# importing the requests library
import requests

import requests
class DangDangUtils(object):
    def __init__ (self,endpoint,token):
        self.endpoint = endpoint
        self.token = token

    def get(self,PARAMS):
        PARAMS["token"] = self.token
        r = requests.get(url=self.endpoint, params=PARAMS)
        return r.json() 

    def daily_sign_in(self):
        return self.get({'action': 'signin'})


# api-endpoint
URL = "http://e.dangdang.com/media/api2.go?"
x = DangDangUtils(URL,'')
 
print(x.daily_sign_in())
