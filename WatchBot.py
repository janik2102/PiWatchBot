import telegram
import json
import os
import datetime

from picamera import PiCamera
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#Read JSON Config with Bot Token and Admin-Identity
configuration = json.load('configuration.json')

token = configuration.get('token')
admin = configuration.get('admin')
vidpath = configuration.get('vidpath')
picpath = configuration.get('picpath')
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
        tmpfile = makepicture()
        update.message.reply_photo(photo=open(tmpfile, 'rb'))
        deletefile(tmpfile)


def video(bot, update):
    if (isAdmin(update.message.chat.username)):
        update.message.reply_text('Video of the room.')


#Define Methods
#check if user is admin
def isAdmin(identity):
    return admin.get('username') == identity

#make video and return the filepath
def makevideo():
    currentTime = datetime.datetime.now()
    path = vidpath + '/' + currentTime + '.h264'
    camera.start_recording(path)
    sleep(10)
    camera.stop_recording()
    return path

#make picture and return the filepath
def makepicture():
    currentTime = datetime.datetime.now()
    path = picpath + '/' + currentTime + 'jpg'
    camera.capture(path)
    return path

#delete file in filesystem
def deletefile(path):
    os.remove(path)

updater = Updater(token)
updater.dispatcher.add_handler(CommandHandler('on', on))
updater.dispatcher.add_handler(CommandHandler('off', off))
updater.dispatcher.add_handler(CommandHandler('picture', picture))
updater.dispatcher.add_handler(CommandHandler('video', video))

#Start the Bot
updater.start_polling()
updater.idle()

