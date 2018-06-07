import telegram
import json

from picamera import PiCamera
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#Read JSON Config with Bot Token and Admin-Identity
with open('Configuration.json') as config_json:
    configuration = json.load(config_json)

token = configuration.get('token')
admin = configuration.get('admin')
videopath = configuration.get('vidpath')
picturepath = configuration.get('picpath')
temppath = configuration.get('temppath')
systemon = True
camera = PiCamera()

#Define User Commands
def on(bot, update):
    if (isAdmin(update.message.chat.username)):
        systemon = True
        update.message.reply_text('Watchsystem activated.')

def off(bot, update):
    if (isAdmin(update.message.chat.username)):
        systemon = False
        update.message.reply_text('Watchsystem deactivated.')

def picture(bot, update):
    if (isAdmin(update.message.chat.username)):
        update.message.reply_text('Picture of the room.')

def video(bot, update):
    if (isAdmin(update.message.chat.username)):
        update.message.reply_text('Video of the room.')
        camera.start_recording(temppath + '/tmpvid.h264')
        sleep(10)
        camera.stop_recording()
        bot.sendVideo(update.message.chat_id, temppath + '/tmpvid.h264')

#Define Methods
def isAdmin(identity):
    return admin.get('username') == identity

updater = Updater(token)
updater.dispatcher.add_handler(CommandHandler('on', on))
updater.dispatcher.add_handler(CommandHandler('off', off))
updater.dispatcher.add_handler(CommandHandler('picture', picture))
updater.dispatcher.add_handler(CommandHandler('video', video))

#Start the Bot
updater.start_polling()
updater.idle()

