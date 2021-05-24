from flask import Flask, redirect, session
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time 

def initDriver():
    chrome_driver_path = 'chromedriver.exe'

    chrome_options = Options()
    chrome_options.add_argument('--headless')

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    return webdriver.Chrome(
        executable_path=chrome_driver_path, options=chrome_options,desired_capabilities=caps
    )

def getLogs(webdriver,url):
    with webdriver as driver:
        try:
            driver.get(url)

            time.sleep(1)
            browser_log = driver.get_log('performance') 
            events = [process_browser_log_entry(entry) for entry in browser_log]
            # must close the driver after task finished
            driver.close()
            return events
        except Exception as e:
            print(e)

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

configs = [
    ["http://m.iptv345.com/?act=play&tid=gt&id=9","http://wowza-live.edge-global.akamai.tvb.com/newslive/smil:mobile_inews.smil/playlist.m3u8?hdnea=st="],
    ["http://www.aiyads.com/zhujiang.html","http://nclive.grtn.cn/zjpd/sd/live.m3u8?_upt="]
]

def stream(stream_id):
    start_time = time.time()
    if(stream_id > len(configs) - 1):
        return "No stream found"

    stream_session = str(stream_id)

    
    webdriver = initDriver()
    ori_url = configs[stream_id][0]

    log("[/stream "+ stream_session +"] fetching:", ori_url)
    events = getLogs(webdriver, ori_url)
    print("M --- %s seconds ---" % (time.time() - start_time))
    # events = [event for event in events if 'Network.responseReceived' in event['method'] and 'response' in event['params'] and 'url' in event['params']['response'] and configs[stream_id][1] in event['params']['response']['url']] 
    # events = [event for event in events if 'url' in event['params']['response']]
    # events = [event for event in events if configs[stream_id][1] in event['params']['response']['url']]
    
    match_url = []
    for event in events:
        try:
            if configs[stream_id][1] in event['params']['response']['url']:
                match_url.append(event['params']['response']['url']) 
        except KeyError:
            continue
    
    if len(match_url) > 0:
        rdir_url= match_url[0]

        log("[/stream "+ stream_session +"] return:",rdir_url)
        print("E --- %s seconds ---" % (time.time() - start_time))

def stream2(stream_id):
    start_time = time.time()
    if(stream_id > len(configs) - 1):
        return "No stream found"

    stream_session = str(stream_id)

    
    webdriver = initDriver()
    ori_url = configs[stream_id][0]

    log("[/stream "+ stream_session +"] fetching:", ori_url)
    events = getLogs(webdriver, ori_url)
    print("M --- %s seconds ---" % (time.time() - start_time))
    events = [event for event in events if 'Network.responseReceived' in event['method'] and 'response' in event['params'] and 'url' in event['params']['response'] and configs[stream_id][1] in event['params']['response']['url']] 
    
    if len(events) > 0:
        rdir_url= events[0]['params']['response']['url']

        log("[/stream "+ stream_session +"] return:",rdir_url)
        print("E --- %s seconds ---" % (time.time() - start_time))

def log(title,message):
    print(str(title) +" "+ str(message))

if __name__ == '__main__':
    stream2(1)


