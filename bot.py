#!/usr/bin/env python
# v0.1.1
# fix merge
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from database import Database

import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'ab_settings')
sys.path.append(CONFIG_DIR)

import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

db = Database()


# Callback function for the /start CommandHandler
def start(bot, update):
    greet_user_name = update.message.from_user.first_name
    bot.send_message(chat_id=update.message.chat_id,
                     text=("Hi {}! I'm here to help you keep track of your "
                           "homework assignments. \n\n"
                           "To get started, just send me an assignment. It's "
                           "that simple! \n\n"
                           "After you've finished an assignment send /done "
                           "to remove it from the list."
                           ).format(
                         greet_user_name)
                     )


# Callback function for the /done CommandHandler
def done(bot, update):
    student = update.message.chat_id
    work_list = [hw.assignment for hw in db.get_due_assignments(student)]
    reply_markup = ReplyKeyboardMarkup(
        build_menu(get_data_buttons(work_list),
                   n_cols=2), one_time_keyboard=True)
    bot.send_message(chat_id=student,
                     text="Which item did you complete?",
                     reply_markup=reply_markup)


# Callback function for the /echo MessageHandler
def echo(bot, update):
    student = update.message.chat_id
    text = update.message.text
    match = db.process_homework(student, text)
    if match is True:
        bot.send_message(chat_id=student,
                         text=('Added "{}" to your completed assignments!'
                               .format(text)
                               )
                         )
        work_list = [hw.assignment for hw in db.get_due_assignments(student)]
    else:
        work_list = [hw.assignment for hw in db.get_due_assignments(student)]

    echo_message = '\n'.join(work_list)
    bot.send_message(chat_id=student,
                     text=echo_message)


# Helper function to build ReplyMarkupKeyboard
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# Helper function to build  button array for ReplyMarkupKeyboard
def get_data_buttons(data):
    button_list = [s for s in data]
    return button_list


# Helper function to get homework assignments for owner.
# def get_user_assignments(owner):
#     homework = []
#     for hw, in session.query(
#             Assignment.assignment).filter(Assignment.owner == owner):
#         homework.append(hw)
#     return homework


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=settings.TOKEN)

    # Get the dispatcher to register handlers.
    dispatcher = updater.dispatcher

    # Add start command handler to collect user data.
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(Filters.text, echo)
    done_handler = CommandHandler('done', done)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(done_handler)

    # Start the Bot.
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
