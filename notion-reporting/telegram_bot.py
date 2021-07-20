import json
import logging
import datetime
import sys
import datetime
import schedule
import requests
from threading import Thread
import time
from notion.client import NotionClient
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

'''
BOT HANDLER v0.01

CONSTANTS
'''
LOG_FILE = 'logs/error.log'
CONFIG_FILE = 'config.json'
CONFIG = {}

PENDING_MODIFY = []

'''
INIT
'''
# Enable logging
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)
    f.close()

'''
COMMAND HANDLERS
'''

# /start


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='你好，我是机器人管家🤗')

# /bills


def billing_report(update, context):
    try:
        if not is_chat_valid(str(update.effective_chat.id)):
            return context.bot.send_message(chat_id=update.effective_chat.id, text='无权限')
        logger.debug(update.effective_chat.id)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=get_bills())
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='404错误')


def get_bills():
    year = datetime.datetime.now().strftime('%Y')
    mth = datetime.datetime.now().strftime('%b')
    two_mth = datetime.datetime.now() - datetime.timedelta(days=60)

    filter_params = {
        'filters': [
            {
                'property': 'WG:@',
                'filter': {
                    'operator': 'date_is_after',
                    'value': {
                        'type': 'exact',
                        'value': {
                            'type': 'date',
                            'start_date': two_mth.strftime('%Y-%m-%d')
                        }
                    }
                }
            }
        ],
        'operator': 'and'
    }

    sort_params = [
        {
            'property': '}uqb',
            'direction': 'descending'
        },
        {
            'property': 'PHJ^',
            'direction': 'descending'
        }
    ]

    result = bill_record_cv.build_query(
        filter=filter_params, sort=sort_params).execute()
    logger.debug(result)

    ele_change, wat_change, gas_change = 0, 0, 0
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
---------------
总: ${}
'''.format(
        year,
        convert_mth(mth),
        str(result[0].electricity_usage), format_change(
            ele_change), str(result[0].electricity_fee),
        str(result[0].water_usage), format_change(wat_change),
        str(result[0].gas_usage), format_change(gas_change),
        f'{result[0].refuse_removal:.2f}',
        f'{result[0].sp_total:.2f}',
        f'{result[0].internet:.2f}',
        f'{(result[0].electricity_fee + result[0].sp_total + result[0].internet):.2f}'
    )

    logger.info(result)
    return report

# /options

options_keyboard = []

def options(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info('User %s started the conversation.', user.first_name)

    options_keyboard = []
    
    for idx, op in enumerate(CONFIG['bot_data']['options']):
        options_keyboard.append(
            [InlineKeyboardButton(op['title'], callback_data=str(idx))],
        )

    options_keyboard.append(
        [InlineKeyboardButton('结束', callback_data=str(len(options_keyboard)))]
    )

    reply_markup = InlineKeyboardMarkup(options_keyboard)
    update.message.reply_text('选择服务:', reply_markup=reply_markup)
    return 0


def get_wifi(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    msg = CONFIG['bot_data']['options'][0]['message'].replace(
        r"<br>", "\n") + "可显示时间为3分钟。"

    query.edit_message_text(
        text=msg
    )

    PENDING_MODIFY.append({
        "action": "update",
        "message_id": query.message.message_id,
        "chat_id": query.message.chat_id,
        "reply": "时间到, 再见！",
        "time": datetime.datetime.now() + datetime.timedelta(minutes=3),
    })

    return ConversationHandler.END

def get_exchange(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    response = requests.get(CONFIG['bot_data']['endpoints']['currency'])
    msg = ""
    if response.status_code != 200:
        msg = "连接错误：" + str(response.status_code)
    else:
        re = response.json()['rates']
        rates = [
            re['CNY']/re['SGD'],
            re['USD']/re['SGD'],
            re['HKD']/re['SGD'],
            re['TWD']/re['SGD']
        ]
        msg ='''
新币兑换率:
---------------
人民币: {}
美元  : {}
港币  : {}
新台币: {}
    '''.format(
        f'{rates[0]:.4f}',
        f'{rates[1]:.4f}',
        f'{rates[2]:.4f}',
        f'{rates[3]:.4f}'
    )
    reply_markup = InlineKeyboardMarkup(options_keyboard)
    query.edit_message_text(msg, reply_markup=reply_markup)
    return 0

def get_weather(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    response = requests.get(CONFIG['bot_data']['endpoints']['weather'])
    if response.status_code != 200:
        msg = "连接错误：" + str(response.status_code)
    else:
        re = response.json()
        lat, lon = re["coord"]
        weather = re["weather"][0]["description"]
        tmp = re["main"]["temp"]
        msg ='''
        未开通
        '''
        msg = '''
新加坡天气: {} {}度
---------------
未开通
        '''.format(weather,tmp)
    reply_markup = InlineKeyboardMarkup(options_keyboard)
    query.edit_message_text(msg, reply_markup=reply_markup)
    return 0

def end(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.edit_message_text(text="再见！")
    return ConversationHandler.END


'''
HELPER FUNCTIONS
'''


def is_chat_valid(chat_id: str):
    if 'chat_ids' in CONFIG['bot_data']:
        if chat_id in CONFIG['bot_data']['chat_ids']:
            return True

    logger.debug('Invalid id: {chat_id}')
    return False


def format_change(value: int):
    msg = ''
    if value > 0:
        msg = '+'
    return msg + '{}%'.format(str(round(value)))


def convert_mth(mth: str):
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


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


def schedule_task():
    global PENDING_MODIFY

    if len(PENDING_MODIFY) > 0:
        for item in PENDING_MODIFY:
            if(datetime.datetime.now() >= item['time']):
                if item['action'] == 'update':
                    bot.editMessageText(
                        chat_id=item['chat_id'],
                        message_id=item['message_id'],
                        text=item['reply'])
                    item['action'] = "done"
                    logger.info("message {} updated".format(
                        item['message_id']))

    PENDING_MODIFY = [
        item for item in PENDING_MODIFY if item['action'] != "done"]


'''=========================================================================='''


def main() -> None:
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    billing_report_handler = CommandHandler('bills', billing_report)
    dispatcher.add_handler(billing_report_handler)

    option_states = []
    for idx, op in enumerate(CONFIG['bot_data']['options']):
        option_states.append(CallbackQueryHandler(
            globals()[op['function']], pattern='^' + str(idx) + '$'))
    option_states.append(CallbackQueryHandler(
        end, pattern='^' + str(len(option_states)) + '$'))

    options_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('options', options)],
        states={
            0: option_states
        },
        fallbacks=[CommandHandler('options', options)],
    )

    dispatcher.add_handler(options_conv_handler)

    schedule.every(1).minutes.do(schedule_task)
    Thread(target=schedule_checker).start()

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    global bot, bill_record_cv

    updater = Updater(token=CONFIG['bot_token'], use_context=True)
    dispatcher = updater.dispatcher
    bot = Bot(token=CONFIG['bot_token'])
    client = NotionClient(token_v2=CONFIG['token'])
    bill_record_cv = client.get_collection_view(CONFIG['bill_record_table'])

    if len(sys.argv) > 1:
        if sys.argv[1] == 'bills':
            text = get_bills()
            bot.sendMessage(
                chat_id=CONFIG['bot_data']['chat_ids'][0], text=text)
    else:
        main()
