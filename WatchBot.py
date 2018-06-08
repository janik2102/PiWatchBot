###########################################################################################
#Imports
###########################################################################################
import telegram
import json
import os
import datetime
import RPi.GPIO as GPIO

from picamera import PiCamera
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

###########################################################################################
#Initialisation
###########################################################################################

#Read JSON Config with Bot Token and Admin-Identity
configuration = json.load(open('configuration.json'))
token = configuration.get('token')
admin = configuration.get('admin')
vidpath = configuration.get('vidpath')
picpath = configuration.get('picpath')
temppath = configuration.get('temppath')

#General System
watchbot = telegram.Bot(token)
systemon = True
motioncounter = 0

#Camera
camera = PiCamera()

#Motion Sensor
motionpin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(motionpin, GPIO.IN)

###########################################################################################
#Define User Commands
###########################################################################################

#Activate the watchbot
def on(bot, update):
    if (isAdmin(update.message.chat.username)):
        if(not systemon):
            print('Watchsystem activated.')
            motioncounter = 0
            systemon = True
            update.message.reply_text('Watchsystem activated.')
        if(systemon):
            print('Watchsystem already activated')
            update.message.reply_text('Watchsystem already activated')

#Deactivate the watchbot
def off(bot, update):
    if (isAdmin(update.message.chat.username)):
        if(systemon):
            print('Watchsystem deactivated.')
            systemon = False
            update.message.reply_text('Watchsystem deactivated.')
        if(not systemon):
            print('Watchsystem already deactivated.')
            update.message.reply_text('Watchsystem already deactivated')

#Get Picture of the room
def picture(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Make Picture of the room.')
        tmppicture = makepicture()
        bot.send_chat_action(update.message.chat.id, action=telegram.ChatAction.UPLOAD_PHOTO)
        update.message.reply_photo(photo=open(tmppicture, 'rb'))
        deletefile(tmppicture)

#Save Picture of the romm
def savePicture(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Save Picture of the room.')
        tmppicture = makepicture()
        update.message.reply_text('Picture saved as: \"' + tmppicture + '\"')

#Get Video of the room
def video(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Make Video of the room.')
        bot.send_chat_action(update.message.chat.id, action=telegram.ChatAction.RECORD_VIDEO)
        tmpvideo = makevideo()
        bot.send_chat_action(update.message.chat.id, action=telegram.ChatAction.UPLOAD_VIDEO)
        update.message.reply_video(video=open(tmpvideo, 'rb'))
        deletefile(tmpvideo)

#Save Video of the room
def saveVideo(bot, update):
    if (isAdmin(update.message.chat.username)):
        print('Save Video of the room.')
        bot.send_chat_action(update.message.chat.id, action=telegram.ChatAction.RECORD_VIDEO)
        tmpvideo = makevideo()
        update.message.reply_text('Video saved as: \"' + tmpvideo + '\"')

###########################################################################################
#Define Methods
###########################################################################################

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

#Callback if motion is detected
def motion_callback(channel):
    global systemon
    if (systemon):
        global motioncounter
        motioncounter += 1
        detectionstring = 'Motion detected! #' + str(motioncounter)
        print(detectionstring)
        watchbot.send_message(admin.get('id'), detectionstring)
        print('Make Picture of the room.')
        tmppicture = makepicture()
        watchbot.send_chat_action(admin.get('id'), action=telegram.ChatAction.UPLOAD_PHOTO)
        watchbot.send_photo(photo=open(tmppicture, 'rb'))
        deletefile(tmppicture)


###########################################################################################
#Main Code
###########################################################################################

updater = Updater(token)
updater.dispatcher.add_handler(CommandHandler('on', on))
updater.dispatcher.add_handler(CommandHandler('off', off))
updater.dispatcher.add_handler(CommandHandler('picture', picture))
updater.dispatcher.add_handler(CommandHandler('savepicture'), savePicture)
updater.dispatcher.add_handler(CommandHandler('video', video))
updater.dispatcher.add_handler(CommandHandler('savevideo', video))

try:
    #Start the Updater
    updater.start_polling()

    #Detecting Motion
    GPIO.add_event_detect(motionpin, GPIO.RISING, callback=motion_callback)

    updater.idle()
except KeyboardInterrupt:
    print('Exit.')
    GPIO.cleanup()
    updater.stop()

