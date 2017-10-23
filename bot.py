from sqlalchemy.orm import sessionmaker
from models import db_connect, map_tables, Assignment, User
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

import logging
import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

engine = db_connect()
map_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Callback function for the /start CommandHandler
def start(bot, update):
    user_data = update.message.from_user
    session.add(User(id=user_data.id,
                     is_bot=user_data.is_bot,
                     first_name=user_data.first_name,
                     last_name=user_data.last_name,
                     username=user_data.username,
                     language_code=user_data.language_code))
    session.commit()
    bot.send_message(chat_id=update.message.chat_id,
                     text="I'm a bot, please talk to me!")


# Callback function for the /done CommandHandler
def done(bot, update):
    chat = update.message.chat_id
    assignments = get_user_assignments(chat)
    reply_markup = ReplyKeyboardMarkup(
        build_menu(get_data_buttons(assignments),
                   n_cols=2), one_time_keyboard=True)
    bot.send_message(chat_id=chat,
                     text="Which item did you complete?",
                     reply_markup=reply_markup)


# Callback function for the /echo MessageHandler
def echo(bot, update):
    chat = update.message.chat_id
    text = update.message.text
    assignments = get_user_assignments(chat)
    if text in assignments:
        session.query(Assignment).filter(Assignment.assignment == text,
                                         Assignment.owner == chat).delete()
        session.commit()
        bot.send_message(chat_id=chat,
                         text=f'Removed "{text}" from your list of assignments')
        assignments = get_user_assignments(chat)
    else:
        session.add(Assignment(assignment=text, owner=chat))
        session.commit()
        assignments = get_user_assignments(chat)

    complete = '\n'.join(assignments)
    bot.send_message(chat_id=chat,
                     text=complete)


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
def get_user_assignments(owner):
    homework = []
    for hw, in session.query(
            Assignment.assignment).filter(Assignment.owner == owner):
        homework.append(hw)
    return homework


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
