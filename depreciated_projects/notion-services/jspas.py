import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import os, sys
from notion_controller import NotionController
import json

"""
v0.01
"""
global config
with open(sys.argv[1]) as json_f:
    config = json.load(json_f)

updater = Updater(token=config["bot_token"], use_context=True)
controller = NotionController(config["notion_token"], False)
dispatcher = updater.dispatcher

logging.basicConfig(filename=config["log_file"],format=config["log_format"],
                    level=logging.INFO)

start_keyboard_markup = ReplyKeyboardMarkup([["/gen_detail"]],
                                            one_time_keyboard=True,
                                            resize_keyboard=True)

# Conversation states
GEN_DETAIL, WRITE_DETAIL = range(2)

# /start


def start_command_handler(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Available Options:", reply_markup=start_keyboard_markup)

# /gen_detail


def gen_detail_command_handler(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Send me the text.")
    return GEN_DETAIL


def gen_detail_data_handler(update, context):
    data = update.message.text

    # convert detail text to json
    details = controller.text_to_json_detail_list(data)
    if len(details) > 0:
        context.user_data["details"] = details

        rex = json.dumps(list(map(lambda x: x.__dict__, details)), indent=4)
        context.bot.send_message(chat_id=update.effective_chat.id, text=rex)

        confirmation_keyboard_markup = ReplyKeyboardMarkup([["Yes", "No"]],
                                                           one_time_keyboard=True,
                                                           resize_keyboard=True)

        update.message.reply_text(
            f"Is the detail correct?", reply_markup=confirmation_keyboard_markup)

        return WRITE_DETAIL

    update.message.reply_text(f"No detail under your name found.")
    return ConversationHandler.END


def write_detail_handler(update, context):
    if update.message.text == "Yes":
        details = context.user_data.get("details", [])
        if len(details) > 0:
            update.message.reply_text(
                "Writing {} detail to Notion...".format(len(details)))
            res = list(
                map(lambda x: str(controller.write_detail_object_to_notion(x)), details))
            reply = list(map(lambda x: x.title, res))
            update.message.reply_text(
                str(res) + " successfully written to Notion.")
        else:
            update.message.reply_text("Invalid session, please try again.")

    update.message.reply_text("Bye!", reply_markup=start_keyboard_markup)
    return ConversationHandler.END


gen_detail_handler = ConversationHandler(
    [CommandHandler('gen_detail', gen_detail_command_handler,
                    pass_user_data=True, pass_chat_data=True)],
    {
        GEN_DETAIL: [MessageHandler(Filters.text, gen_detail_data_handler, pass_user_data=True, pass_chat_data=True)],
        WRITE_DETAIL: [MessageHandler(
            Filters.text, write_detail_handler, pass_user_data=True, pass_chat_data=True)]
    },
    [CommandHandler('start', start_command_handler)],
)

dispatcher.add_handler(gen_detail_handler)

dispatcher.add_handler(CommandHandler('start', start_command_handler))


def main(request):
    try:
        updater.start_polling()
        updater.idle()
    except KeyboardInterrupt:
        updater.stop()


if __name__ == "__main__":
    main(None)
