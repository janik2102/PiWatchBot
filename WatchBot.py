import telegram
import json
import os
import datetime

from picamera import PiCamera
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#Read JSON Config with Bot Token and Admin-Identity
configuration = json.load(open('configuration.json'))

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
        print('Watchsystem activated.')
        systemon = True
        update.message.reply_text('Watchsystem activated.')

def off(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Watchsystem deactivated.')
        systemon = False
        update.message.reply_text('Watchsystem deactivated.')

def picture(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Make Picture of the room.')
        tmppicture = makepicture()
        update.message.reply_photo(photo=open(tmppicture, 'rb'))
        deletefile(tmppicture)


def video(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Make Video of the room.')
        tmpvideo = makevideo()
        update.message.reply_video(video=open(tmpvideo, 'rb'))
        deletefile(tmpvideo)


#Define Methods
#check if user is admin
def isAdmin(identity):
    return admin.get('username') == identity

#make video and return the filepath
def makevideo():
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = vidpath + '/' + currentTime + '.h264'
    print('Saving Video to ' + path)
    camera.start_recording(path)
    print('Recording ...')
    sleep(10)
    camera.stop_recording()
    print('Saved successfull')
    return path

#make picture and return the filepath
def makepicture():
    currentTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = picpath + '/' + currentTime + '.jpg'
    print('Saving Photo to ' + path)
    camera.capture(path)
    print('Saved successfull')
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

