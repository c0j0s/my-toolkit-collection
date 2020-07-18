from flask import Flask, redirect, session
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time
# from task_handler import TaskHandler
import sys

# handler = TaskHandler(sys.argv[1])
app = Flask(__name__)

configs = [
    {
        "host": "http://news.tvb.com/live/inews?is_hd",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "http://wowza-live.edge-global.akamai.tvb.com/newslive/"
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "http://wowza-live.edge-global.akamai.tvb.com/newslive/"
            }
        ]
    },
    {
        "host": "http://www.aiyads.com/zhujiang.html",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "http://nclive.grtn.cn/zjpd/sd/live.m3u8?_upt="
            }
        ]
    },
    {
        "host": "http://news.tvb.com/live/inews?is_hd",
        "filters": [
            {
                "method": "Network.requestWillBeSent",
                "type": "request",
                "search": "http://wowza-live.edge-global.akamai.tvb.com/newslive/"
            },
            {
                "method": "Network.responseReceived",
                "type": "response",
                "search": "http://wowza-live.edge-global.akamai.tvb.com/newslive/"
            }
        ]
    }
]


def initDriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(ChromeDriverManager().install(
    ), options=chrome_options, desired_capabilities=caps)
    return driver


def getLogs(webdriver, url):
    with webdriver as driver:
        try:
            driver.get(url)
            browser_log = driver.get_log('performance')
            events = [process_browser_log_entry(
                entry) for entry in browser_log]
            driver.close()
            return events
        except Exception as e:
            print("[Exception] getLogs:" + str(e))


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


@app.route('/<int:stream_id>')
def stream(stream_id):
    webdriver = initDriver()

    start_time = time.time()
    if(stream_id > len(configs) - 1):
        return "No stream found"

    stream_session = str(stream_id)

    if session.get(stream_session) is None:

        ori_url = configs[stream_id]["host"]
        print("[/stream " + stream_session + "] fetching: " + ori_url)
        events = getLogs(webdriver, ori_url)

        for channel in configs[stream_id]["filters"]:
            result = filter_log(events, channel)
            if result is not None:
                session[stream_session] = result
                break
            else:
                print("Channel not found")
                session[stream_session] = "https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8"

    print("E --- %s seconds ---" % (time.time() - start_time))
    print("[/stream " + stream_session + "] return: " +
                  session.get(stream_session))
    return redirect(session.get(stream_session))


@app.route('/delete-session')
def delete_session():
    session.clear()
    print("[/delete-session] return: Session deleted")
    return 'Session deleted'

if __name__ == '__main__':
    app.secret_key = 'stream'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = False
    app.run(host='127.0.0.1', port=5000)
    # app.run(host='0.0.0.0', port=80)
