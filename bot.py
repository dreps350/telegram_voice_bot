#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Stores voice message files to './content/<user_id>/' folder, where user_id is a message sender id.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import yaml
import os
import re

from telegram.ext import Updater, MessageHandler, Filters


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Error handler receives the raised TelegramError object in error.
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def load_token():
    """Load token from file ./config.yaml"""
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["token"]


def capture_voice(bot, update):
    """Capture audio file sent bu user."""
    user_id = update.message.from_user.id
    audio_file = update.message.voice.get_file()  # telegram.File object

    with open(handle_path(user_id), "wb") as f:
        logger.warning(audio_file.download(out=f))


def handle_path(user_id):
    content_dir = "./content/"
    user_dir = os.path.join(content_dir, str(user_id))
    if not os.path.isdir(user_dir):
        os.makedirs(user_dir)

    audio_file_pat = r"audio_message_"

    max_index = 0
    first_file = True
    for root, dirs, files in os.walk(user_dir):
        for f in files:
            matches = re.findall(audio_file_pat + "(\d+)", f)
            if matches:
                first_file = False
                index = int(matches[0])
                if index > max_index:
                    max_index = index

    if not first_file:
        max_index += 1

    new_file_name = "{}{}".format(audio_file_pat, max_index)

    return os.path.join(user_dir, new_file_name)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(load_token())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # audio handler
    dp.add_handler(MessageHandler(Filters.voice, capture_voice))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
