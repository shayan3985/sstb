import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shadabsupervisor.settings")
django.setup()
########################################################################
DEBUG = False
from database.models import Member, Spam, AddLog, BotAdmin
from menuHandler import MenuHandler
from telegram.ext import Updater
import logging, telegram
from telegram.ext import MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler
import datetime
from django.utils import timezone
from button import Button, Method
from telegram import InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

supervisorToken = '446396711:AAEbdidxiCfrhw6usUC64JjPjyKzONvIMJM'
testrobotToken = '311401168:AAGERApOnSg_izqKL2THFBLMniBuhbsINcU'
buttonManager = Button()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
updater = None
bot = None
group = None
if DEBUG:
    updater = Updater(token=testrobotToken)
    bot = telegram.Bot(token=testrobotToken)
    group = -1001135569951
else:
    updater = Updater(token=supervisorToken)
    bot = telegram.Bot(token=supervisorToken)
    group = -1001137298648


dispatcher = updater.dispatcher
menuHandler = MenuHandler()
goodNight = "CAADBAADbxcAAtR-mwVLHopnLOh30wI"
noAds = "CAADBAADnRMAAmFcPgpEoUaR-0iBrwI"
goodMorning = "CAADBAAD0gIAAmFcPgqGkUqd41QPhQI"
ads = ""


# u= telegram.Update()
# m = telegram.Message()
# u = telegram.User()
# u.id
# m.from_user
# m.chat_id
# m.audio
# a = telegram.Audio()
# a.title
# b = telegram.Voice
# b.duration







def deleteBots(bot, update):
    new_members = update.message.new_chat_members
    print(new_members)
    for m in new_members:
        print(m.first_name)
        if m.bot is None:
            print('user')
        else:
            print('bot')
            if m.bot.id is bot.id:
                print(m.bot.id)
                print(bot.id)
                print('my self')


def manage_voice(bot, update):
    if not is_admin(update):
        update.message.forward(chat_id=431282203)
        update.message.delete()


def is_admin(update):
    list = update.message.chat.get_administrators()
    id = update.message.from_user.id
    for cm in list:
        if id == cm.user.id:
            return True
    return False


def manage_audio(bot, update):
    if not is_admin(update):
        update.message.forward(chat_id=431282203)
        update.message.delete()


def manage_sticker(bot, update):
    # 431282203 maman
    print(update.message.sticker.file_id)
    if not is_admin(update):
        bot.send_message(chat_id=431282203,
                         text=str('sticker from ' + str(update.message.from_user.first_name) + '\n' +
                                  ' ' + str(update.message.from_user.last_name) + '\n' + '@'
                                  + str(update.message.from_user.username)))
        update.message.forward(chat_id=431282203)

        update.message.delete()


def all_message(bot  # type: telegram.Bot
                , update  # type:telegram.Update
                ):
    # cq = update.callback_query  # type: telegram.CallbackQuery
    # cq.answer()
    # print(str(cq.message))
    #
    # return
    print(group)
    print(update.message.chat_id)
    if update.message.chat_id != group:
        update.message.delete()
        return
    if isSpam(bot, update) and not is_admin(update):
        update.message.delete()
        return
    if update.message.sticker is not None and not is_admin(update):
        update.message.delete()
        return
    if update.message.audio is not None and not is_admin(update):
        update.message.delete()
        return
    if update.message.voice is not None and not is_admin(update):
        update.message.delete()
        return
    if update.message.video is not None and not is_admin(update):
        update.message.delete()
        return
    print(update.message.sticker)
    new_members = update.message.new_chat_members  # type: list
    if len(new_members) is not 0:
        u = update.message.from_user  # type: telegram.User
        response = ''
        member = None
        try:
            member = Member.objects.get(t_id=update.message.from_user.id)
        except:
            member = Member.objects.create(t_id=update.message.from_user.id)
            member.add_count = 0

        if u.username is not None:
            response = '@' + u.username + '\n'
            member.username = u.username
        if u.first_name is not None:
            response = response + u.first_name + ' '
            member.first_name = u.first_name
        if u.last_name is not None:
            response = response + u.last_name
            member.last_name = u.last_name
        response = response + '\n'
        response = response + 'added :\n'
        for m in new_members:  # type: telegram.User
            response = response + str(m.first_name) + '  ' + str(m.last_name) + '  @' + str(m.username) + '\n'
            log = AddLog.objects.create()
            log.log = response
            log.save()
            newM = None
            try:
                newM = Member.objects.get(t_id=m.id)
            except:
                newM = None
            if newM is None:
                member.add_count = member.add_count + 4
                newM = Member.objects.create(t_id=m.id)
                newM.last_name = m.last_name
                newM.first_name = m.first_name
                newM.username = m.username
                newM.add_count = 0
                newM.save()
        member.save()
    else:
        if not is_admin(update):
            hour = datetime.datetime.now().hour
            if 1 <= hour < 7:
                update.message.forward(chat_id=431282203)
                update.message.delete()
                return
            u = update.message.from_user  # type: telegram.User
            member = None
            try:
                member = Member.objects.get(t_id=u.id)
                print('member found')
            except:
                print('new member')
                member = Member.objects.create(t_id=u.id)
                member.add_count = 0
                member.username = u.username
                member.last_name = u.last_name
                member.first_name = u.first_name
                member.save()
            if member.add_count < 1:
                update.message.delete()
            else:
                if member.last_message_date is not None:
                    lm = member.last_message_date
                    now = timezone.now()
                    span = now - lm  # type: datetime.timedelta
                    shour = span.seconds / (60 * 60)
                    if shour < 3:
                        update.message.delete()
                        return
                member.add_count -= 1
                member.last_message_date = timezone.now()
                member.save()
                # if member.add_count < 3:
                #     update.message.delete()


def isSpam(bot
           , update  # type: telegram.Update
           ):
    return False


def onStart(bot
            , update  # type: telegram.Update
            ):
    bot.send_message(chat_id=update.message.chat_id, text=buttonManager.staticjson['mainMenuText']
                     , reply_markup=buttonManager.generateMainMenuMarkUp())


def ajab(bot,
         update  # type: telegram.Update
         ):
    m = update.message  # type: telegram.Message

    bot.send_message(chat_id=m.chat_id, text='wtf')
    custom_keyboard = [['top-left', 'top-right'],
                       ['bottom-left', 'bottom-right']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=m.chat_id,
                     text="Custom Keyboard Test",
                     reply_markup=reply_markup)


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


def test(bot, update, args):
    m = update.message  # type: telegram.Message

    if len(args) > 0:
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=m.chat_id, text=args[0], reply_markup=reply_markup)
    else:
        button_list = [
            InlineKeyboardButton("test", callback_data='xxx'),
            InlineKeyboardButton("ajab", url='http://yahoo.com'),
            InlineKeyboardButton("row 2", url='http://jjo.ir')
        ]
        print('x')
        print('x')
        print(button_list)
        print(build_menu(button_list, n_cols=2))
        print('x')
        print('x')
        # some_strings = ["col1", "col2", "row2"]
        # button_list = [InlineKeyboardButton(s) for s in some_strings]
        reply_markup = telegram.InlineKeyboardMarkup(build_menu(button_list, n_cols=2))

        bot.send_message(chat_id=m.chat_id, text="A two-column menu", reply_markup=reply_markup)


#

def menuCallBack(bot  # type: telegram.Bot
                 , update):
    cq = update.callback_query  # type: telegram.CallbackQuery
    if cq.data == str(Method.button_help):
        menuHandler.help(bot, update, cq)
    if cq.data == str(Method.button_return):
        menuHandler.mainMenu(bot, update, cq)
    if cq.data == str(Method.button_show_token):
        menuHandler.showToken(bot, update, cq)
    cq.answer()


def isBotAdmin(update):
    id = update.message.from_user.id
    a = None
    try:
        a = BotAdmin.objects.get(t_id=id)
    except:
        a = None
    if a is None:
        return False
    else:
        return True


def shadab(bot,
           update  # type: telegram.Update
           ):  # starting bot
    if not isBotAdmin(update):
        bot.send_message(chat_id=update.message.chat_id, text="hi")
        bot.send_message(chat_id=update.message.chat_id, text="ajab")
        update.message.delete()

    else:

        update.message.delete()


# handler2 = MessageHandler(Filters.voice, manage_voice)
# dispatcher.add_handler(handler2, 1)
# handler3 = MessageHandler(Filters.audio, manage_audio)
# dispatcher.add_handler(handler3, 2)
# handler4 = MessageHandler(Filters.sticker, manage_sticker)
# dispatcher.add_handler(handler4, 3)
handler1 = MessageHandler(Filters.all, all_message)
dispatcher.add_handler(handler1, 4)
# handler5 = CommandHandler('ajab', ajab)
# dispatcher.add_handler(handler5, 4)
# handler6 = CommandHandler('test', test, pass_args=True)
# dispatcher.add_handler(handler6, 5)
# handler7 = CommandHandler('start', onStart)
# dispatcher.add_handler(handler7, 6)
# handler8 = CallbackQueryHandler(menuCallBack)
# dispatcher.add_handler(handler8)

import schedule
import time, _thread


def goodmorning():
    bot.send_sticker(chat_id=group, sticker=goodMorning)


def goodnight():
    bot.send_sticker(chat_id=group, sticker=noAds)
    bot.send_sticker(chat_id=group, sticker=goodNight)


schedule.every().day.at("01:00").do(goodnight)
schedule.every().day.at("07:00").do(goodmorning)


def ca(update):
    bot.send_message(chat_id=update.message.chat_id, text='hyhy')


def threadjob():
    while True:
        schedule.run_pending()
        time.sleep(60)


_thread.start_new_thread(threadjob, ())
updater.start_polling()
