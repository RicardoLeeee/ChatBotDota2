## chatbot.py
from ast import Break
from asyncore import dispatcher
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
# The messageHandler is used for all message updates
import configparser
import logging
from liquipediapy import dota
import redis

global redis1

dota_obj = dota("appname")

players=1
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
    # register a dispatcher to handle message: here we register an echo dispatcher

    
    dispatcher.add_handler(CommandHandler("help", help_command))
    conversation=ConversationHandler(entry_points=[CommandHandler("player", check_player)],
    states={players:[MessageHandler(Filters.text & (~Filters.command), player_check)]},
    fallbacks=[CommandHandler("quit", quit_command)])
    dispatcher.add_handler(conversation)
    dispatcher.add_handler(CommandHandler("like", like))
    # dispatcher.add_handler(CommandHandler("hero", check_hero))
    # dispatcher.add_handler(CommandHandler("item", check_item))
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)


    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    update.message.reply_text('Enter /help to get help')

def help_command(update: Updater, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Please enter /player to check player's details\nEnter /like + Player's name to give a like")

def check_player(update: Updater, context: CallbackContext):
    update.message.reply_text("Starting to check player's details\nEnter player name to check\nEnter /quit to quit")
    return players

# def check_hero(update: Updater, context: CallbackContext):
#     heros = dota_obj.get_heros()
#     for i in range(len(heros)):
#         update.message.reply_text(heros[i])

# def check_item(update: Updater, context: CallbackContext):
#     items = dota_obj.get_items()
#     for i in range(len(items)):
#         update.message.reply_text(items[i])

def like(update: Updater, context: CallbackContext):
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   
        redis1.incr(msg)
        update.message.reply_text('You have liked ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /like <keyword>')

def player_check(update: Updater, context: CallbackContext):
    try:
        player_name=update.message.text
        player_details = dota_obj.get_player_info(player_name,True)
        try:
            message='Name:{}\nNation:{}\nBorn:{}\nTeam:{}\nGame ID:{}'.format(player_details['info']['name'],player_details['info']['nationality'],player_details['info']['born'],player_details['info']['team'],player_details['info']['ids'])
            link_list=[]
            keys=player_details['links'].keys()
            for i in range(len(list(keys))):
                a=[]
                a.append(InlineKeyboardButton(list(keys)[i],url=player_details['links'][list(keys)[i]]))
                link_list.append(a)
            update.message.reply_text(message,reply_markup=InlineKeyboardMarkup(link_list))
            context.bot.send_photo(update.effective_chat.id,player_details['info']['image'] )
        except:
            try:
                message='Name:{}\nNation:{}\nBorn:{}\nGame ID:{}'.format(player_details['info']['name'],player_details['info']['nationality'],player_details['info']['born'],player_details['info']['ids'])
                link_list=[]
                keys=player_details['links'].keys()
                for i in range(len(list(keys))):
                    a=[]
                    a.append(InlineKeyboardButton(list(keys)[i],url=player_details['links'][list(keys)[i]]))
                    link_list.append(a)
                update.message.reply_text(message,reply_markup=InlineKeyboardMarkup(link_list))
                context.bot.send_photo(update.effective_chat.id,player_details['info']['image'] )
            except:
                message='Name:{}\nNation:{}\nBorn:{}'.format(player_details['info']['name'],player_details['info']['nationality'],player_details['info']['born'])
                link_list=[]
                keys=player_details['links'].keys()
                for i in range(len(list(keys))):
                    a=[]
                    a.append(InlineKeyboardButton(list(keys)[i],url=player_details['links'][list(keys)[i]]))
                    link_list.append(a)
                update.message.reply_text(message,reply_markup=InlineKeyboardMarkup(link_list))
                context.bot.send_photo(update.effective_chat.id,player_details['info']['image'] )
    except:
        update.message.reply_text("Can't find this player")


def quit_command(update: Updater, context: CallbackContext):
    update.message.reply_text('Quit')
    return ConversationHandler.END

if __name__ == '__main__':
    main()