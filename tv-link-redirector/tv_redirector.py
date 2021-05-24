from flask import Flask, redirect, session, request
from pytz import HOUR
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.schedulers.background import BackgroundScheduler
import json
import logging
import atexit
import threading

logging.basicConfig(filename="logs/error.log",format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

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

configs = [
    {
        "host": "http://news.tvb.com/live/?is_hd",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "https://prd-vcache.edge-global.akamai.tvb.com/__cl/slocalr2526/__c/ott_C_h264/__op/default/__f/index.m3u8"
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "https://prd-vcache.edge-global.akamai.tvb.com/__cl/slocalr2526/__c/ott_C_h264/__op/default/__f/index.m3u8"
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
                "search": "https://prd-vcache.edge-global.akamai.tvb.com/__cl/slocalr2526/__c/ott_I-FINA_h264/__op/default/__f/index.m3u8"
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "https://prd-vcache.edge-global.akamai.tvb.com/__cl/slocalr2526/__c/ott_I-FINA_h264/__op/default/__f/index.m3u8"
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
                "search": "tcdn.itouchtv.cn/live/gdzj.m3u8"
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "tcdn.itouchtv.cn/live/gdzj.m3u8"
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
        if channel["redirect"] is None and chrome_driver is not None:
            update_stream(stream_id)

        logging.info("[/{}.m3u8 -> {}".format(str(stream_id),channel["redirect"]))
        return redirect(channel["redirect"])
    except Exception as e:
        logging.error(str(configs[stream_id]))
        return redirect("https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8"), 200 

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

        result = None
        for stream in channel["filters"]:
            result = filter_log(events, stream)
            if result is not None:
                return result
        return result
    except Exception as e:
        logging.error("[Exception] getLogs:" + str(e))

def update_stream(stream_id:int = -1):
    global chrome_driver
    chrome_driver = webdriver.Chrome(chrome_engine, options=chrome_options, desired_capabilities=caps)
    if stream_id == -1:
        for idx, channel in enumerate(configs):
            logging.info("Updating stream index: {}".format(idx))
            configs[idx]["redirect"] = get_stream_link(channel)
    else:
        if stream_id < len(configs):
            configs[stream_id]["redirect"] = get_stream_link(configs[stream_id])
        else:
            logging.info("Stream id invalid.")          
    chrome_driver.close()

def main():
    threading.Thread(target=update_stream).start()

# Register task
cron = BackgroundScheduler(daemon=True)
cron.add_job(update_stream, 'interval', hours=6)
cron.start()
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == "__main__":
    # initialise channel
    # main()

    # initialise flask
    app.debug = False
    # app.run(host='127.0.0.1', port=5000)
    app.run(host='0.0.0.0', port=20020)