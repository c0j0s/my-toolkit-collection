from flask import Flask, redirect, session, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import sys
import atexit


from task_handler import TaskHandler
handler = TaskHandler(sys.argv[1])

app = Flask(__name__)
chrome_driver = None
chrome_engine = ChromeDriverManager().install()
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}

locale = "global"

configs = [
    {
        "host": "http://news.tvb.com/live/?is_hd",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "http://wowza-live.edge-{}.akamai.tvb.com/newslive/".format(locale)
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "http://wowza-live.edge-{}.akamai.tvb.com/newslive/".format(locale)
            }
        ],
        "redirect":""
    },
    {
        "host": "https://www.gdtv.cn/tvChannelDetail/44",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "https://nclive.grtn.cn/zjpd/sd/live.m3u8?_upt="
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "https://nclive.grtn.cn/zjpd/sd/live.m3u8?_upt="
            }
        ],
        "redirect":""
    },
    {
        "host": "http://news.tvb.com/live/j5_ch85?is_hd",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "http://wowza-live.edge-{}.akamai.tvb.com/newslive/smil:mobilehd_finance.smil/playlist.m3u8".format(locale)
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "http://wowza-live.edge-{}.akamai.tvb.com/newslive/smil:mobilehd_finance.smil/playlist.m3u8".format(locale)
            }
        ],
        "redirect":""
    }
]

# Flask methods
@app.route('/<int:stream_id>.m3u8')
def stream(stream_id:int):
    try:
        channel = configs[stream_id]
        if channel["redirect"] == "":
            channel["redirect"] = get_stream_link(channel)

        handler.print("[/{}.m3u8 -> {}".format(str(stream_id),channel["redirect"]))
        return redirect(channel["redirect"])
    except Exception as e:
        handler.print(str(e))
        return "404", 404 

@app.route('/update')
def update():
    update_stream()
    return json.dumps(configs)

@app.errorhandler(404)
def http_error_handler(error):
    return "404", 404

# local methods
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

def get_stream_link(channel):
    try:
        chrome_driver.get(channel["host"])
        browser_log = chrome_driver.get_log('performance')
        events = [process_browser_log_entry(entry) for entry in browser_log]
        
        
        result = ""
        for stream in channel["filters"]:
            result = filter_log(events, stream)
            if result is not None:
                return result
            else:
                result = "https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8"

        return result
    except Exception as e:
        handler.print("[Exception] getLogs:" + str(e))

def update_stream():
    chrome_driver = webdriver.Chrome(chrome_engine, options=chrome_options, desired_capabilities=caps)
    for idx, channel in enumerate(configs):
        handler.print("Updating stream index: {}".format(idx))
        configs[idx]["redirect"] = get_stream_link(channel)
    chrome_driver.close()

def main():
    update_stream()

if __name__ == "__main__":
    # Register task
    cron = BackgroundScheduler(daemon=True)
    cron.add_job(update_stream, 'cron', hour=15)
    cron.start()
    atexit.register(lambda: cron.shutdown(wait=False))
    
    # initialise channel
    main()

    # initialise flask
    app.debug = False
    # app.run(host='127.0.0.1', port=5000)
    app.run(host='0.0.0.0', port=80)