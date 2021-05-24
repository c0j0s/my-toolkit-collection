from flask import Flask, redirect, session
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time 

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def filter_log(events, channel):
    result = [event for event in events if channel["method"] in event['method'] and channel["type"] in event['params']
              and 'url' in event['params'][channel["type"]] and channel["search"] in event['params'][channel["type"]]['url']]
    if len(result) > 0:
        return str(result[0]['params'][channel["type"]]['url'])
    else:
        return None

def getLogs(webdriver, url):
    with webdriver as driver:
        try:
            driver.get(url)
            browser_log = driver.get_log('performance')
            events = [process_browser_log_entry(
                entry) for entry in browser_log]
            # must close the driver after task finished
            driver.close()
            return events
        except Exception as e:
            print("[Exception] getLogs:", str(e))

def initDriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument(
    #     '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148')

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(ChromeDriverManager().install(
    ), options=chrome_options, desired_capabilities=caps)
    return driver

configs = [
    {
        "host": "https://www.gdtv.cn/tvChannelDetail/44",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "tcdn.itouchtv.cn/live/gdzj.m3u8"
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "tcdn.itouchtv.cn/live/gdzj.m3u8"
            }
        ],
        "redirect":""
    },
    {
        "host": "https://www.gdtv.cn/tvChannelDetail/82",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "dslive.grtn.cn/hyzh/sd/live.m3u8?_upt="
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "dslive.grtn.cn/hyzh/sd/live.m3u8?_upt="
            }
        ],
        "redirect":""
    }
]

webdriver = initDriver()
ori_url = configs[1]["host"]
events = getLogs(webdriver, ori_url)
with open("log.txt", "w") as f:
    f.write(str(events))
    f.close()
for channel in configs[0]["filters"]:
    result = filter_log(events, channel)
    if result is not None:
        print(result)
# webdriver.close()
webdriver.quit()