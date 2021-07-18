from telegram.ext import Updater, CommandHandler
from telegram import Bot
from notion.client import NotionClient
import json
import logging
import datetime
import sys

'''
BOT HANDLER v0.01

CONSTANTS
'''
LOG_FILE = 'logs/error.log'
CONFIG_FILE = 'config.json'
CONFIG = {}

'''
INIT
'''
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)
    f.close()

    updater = Updater(token=CONFIG['bot_token'], use_context=True)
    dispatcher = updater.dispatcher
    bot = Bot(token=CONFIG['bot_token'])
    client = NotionClient(token_v2=CONFIG['token'])
    bill_record_cv = client.get_collection_view(CONFIG['bill_record_table'])

'''
COMMAND HANDLERS
'''

# /start


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='你好，我是机器人管家🤗')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# /bills


def billing_report(update, context):
    try:
        logging.debug(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, text=get_bills())
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="404错误")


billing_report_handler = CommandHandler('bills', billing_report)
dispatcher.add_handler(billing_report_handler)

def get_bills():
    year = datetime.datetime.now().strftime('%Y')
    mth = datetime.datetime.now().strftime('%b')
    two_mth = datetime.datetime.now() - datetime.timedelta(days=60)

    filter_params = {
        "filters": [
            {
                "property": "WG:@",
                "filter": {
                    "operator": "date_is_after",
                    "value": {
                        "type": "exact",
                        "value": {
                            "type": "date",
                            "start_date": two_mth.strftime('%Y-%m-%d')
                        }
                    }
                }
            }
        ],
        "operator": "and"
    }

    sort_params = [
        {
            "property": "}uqb",
            "direction": "descending"
        },
        {
            "property": "PHJ^",
            "direction": "descending"
        }
    ]

    result = bill_record_cv.build_query(
        filter=filter_params, sort=sort_params).execute()
    logging.debug(result)

    ele_change, wat_change, gas_change = 0,0,0
    if len(result) > 1:
        ele_change = (float(result[0].electricity_usage) -
                      float(result[1].electricity_usage))/float(result[1].electricity_usage) * 100
        wat_change = (float(result[0].water_usage) -
                      float(result[1].water_usage))/float(result[1].water_usage) * 100
        gas_change = (float(result[0].gas_usage) -
                      float(result[1].gas_usage))/float(result[1].gas_usage) * 100

    report = '''
{} {}月能源报告

电: {}kwh ({})
     ${}

水: {}cu3 ({}) 
气: {}cu3 ({}) 
杂: ${}
     ${}

网: ${}
=====================
总: ${}
'''.format(
        year,
        convert_mth(mth),
        str(result[0].electricity_usage), format_change(ele_change),str(result[0].electricity_fee),
        str(result[0].water_usage), format_change(wat_change),
        str(result[0].gas_usage), format_change(gas_change),
        f'{result[0].refuse_removal:.2f}',
        f'{result[0].sp_total:.2f}',
        f'{result[0].internet:.2f}',
        f'{(result[0].electricity_fee + result[0].sp_total + result[0].internet):.2f}'
        )
    
    logging.info(result)
    return report

# /uc


'''
HELPER FUNCTIONS
'''


def format_change(value):
    msg = ""
    if value > 0:
        msg = "+"
    return msg + "{}%".format(str(round(value)))


def convert_mth(mth):
    if mth == 'Jan':
        return '一'
    elif mth == 'Feb':
        return '二'
    elif mth == 'Mar':
        return '三'
    elif mth == 'Apr':
        return '四'
    elif mth == 'May':
        return '五'
    elif mth == 'Jun':
        return '六'
    elif mth == 'Jul':
        return '七'
    elif mth == 'Aug':
        return '八'
    elif mth == 'Sep':
        return '九'
    elif mth == 'Oct':
        return '十'
    elif mth == 'Nov':
        return '十一'
    elif mth == 'Dec':
        return '十二'


'''=========================================================================='''
if len(sys.argv) > 1:
    if sys.argv[1] == 'bills':
        text = get_bills()
        chat_id = -462282830 # test group
        #chat_id = 0 # production
        bot.sendMessage(chat_id=chat_id, text=text)
else:
    updater.start_polling()
