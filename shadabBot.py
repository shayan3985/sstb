import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shadabsupervisor.settings")
django.setup()
########################################################################
DEBUG = False
from database.models import Member, Spam, AddLog, BotAdmin, Governor, Post
from telegram.ext import Updater
import logging, telegram
from MessageHelper import MessageHelper
from telegram.ext import messagequeue as mq
from MQBot import MQBot
from telegram.ext import MessageHandler, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler
import datetime, base64
from django.utils import timezone
import datetime

supervisorToken = '446396711:AAEbdidxiCfrhw6usUC64JjPjyKzONvIMJM'
testrobotToken = '311401168:AAGERApOnSg_izqKL2THFBLMniBuhbsINcU'
mainGroupID = -1001137298648
testGroupID = -1001135569951
mainLogChannel = -1001244112411
testLogChannel = -1001179670296

goodNightStickerID = "CAADBAADbxcAAtR-mwVLHopnLOh30wI"
noAdsStickerID = "CAADBAADnRMAAmFcPgpEoUaR-0iBrwI"
goodMorningStickerID = "CAADBAAD0gIAAmFcPgqGkUqd41QPhQI"

shayanTID = 389224229
nasrinTID = 431282203
night_time = False
private_party = False
private_party_duration = None
private_party_start_time = None  # type: datetime
private_party_owner = None
private_party_owner_name = None

first_message_id_file_name = "firstMessage"
if not os.path.exists("./" + first_message_id_file_name):
    with open("./" + first_message_id_file_name, 'w') as f:
        f.write("0")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

messageHelper = MessageHelper()
bot = None
group = None
updater = None
log_channel = None
q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
if DEBUG:
    log_channel = testLogChannel
    bot = MQBot(token=testrobotToken, mqueue=q)
    updater = Updater(token=testrobotToken)
    group = testGroupID
else:
    log_channel = mainLogChannel
    bot = MQBot(token=supervisorToken, mqueue=q)
    updater = Updater(token=supervisorToken)
    group = mainGroupID

last_morning_call = None
last_night_call = None


def is_master(id):
    if id == shayanTID:
        return True
    if not DEBUG:
        if id == nasrinTID:
            return True
    return False


def is_admin(update):
    if is_master(update.message.from_user):
        return True
    list = update.message.chat.get_administrators()
    id = update.message.from_user.id
    for cm in list:
        if id == cm.user.id:
            return True
    return False


def is_governor(id):
    if is_master(id):
        return True
    try:
        u = Governor.objects.get(t_id=id)
        if u is not None:
            return True
    except:
        pass
    return False


def is_spam(message  # type: telegram.Message
            ):
    return False


def all_text(bot  # type: telegram.Bot
             , update  # type: telegram.Update
             ):
    if update is None:
        return
    if update.message is None:
        return
    if update.message.chat.type == telegram.Chat.PRIVATE:
        private_text(bot, update)
    elif update.message.chat.type == telegram.Chat.CHANNEL:
        channel_text(bot, update)
    elif update.message.chat.type == telegram.Chat.GROUP or update.message.chat.type == telegram.Chat.SUPERGROUP:
        group_text(bot, update)


def group_text(bot  # type: telegram.Bot
               , update  # type: telegram.Update
               ):
    global night_time
    message = update.message  # type: telegram.Message
    if message.chat_id != group:
        try:
            message.delete()
        except:
            pass
        return
    if is_admin(update) or is_governor(update.message.from_user.id):
        return
    if is_spam(message) and not is_admin(update):
        message.forward(chat_id=log_channel)
        # bot.send_message(chat_id=log_channel,text="hihi",reply_to_message_id=forwarded_message.message_id)
        message.delete()
        return
    if not private_party and not party_time_check():
        if update.message.sticker is not None and not is_admin(update):
            message.forward(chat_id=log_channel)
            update.message.delete()
            return
        if update.message.video is not None and not is_admin(update):
            message.forward(chat_id=log_channel)
            update.message.delete()
            return
    if update.message.audio is not None and not is_admin(update):
        message.forward(chat_id=log_channel)
        update.message.delete()
        return
    if update.message.voice is not None and not is_admin(update):
        message.forward(chat_id=log_channel)
        update.message.delete()
        return

    new_members = update.message.new_chat_members  # type: list
    if len(new_members) is not 0:
        manage_new_members_update(bot, update, new_members)
    else:
        if not is_admin(update):
            if night_time:
                update.message.forward(chat_id=log_channel)
                update.message.delete()
                return
            group_text_permission_control(bot, update)


def party_time_check():
    global private_party_start_time
    global private_party_duration
    if private_party_duration is None or private_party_start_time is None:
        return False
    if (datetime.datetime.now() - private_party_start_time).total_seconds() / 3600 < private_party_duration:
        return True
    return False


def group_text_permission_control(bot  # type: telegram.Bot
                                  , update  # type: telegram.Update
                                  ):
    global private_party
    global private_party_owner
    # private party

    if private_party:
        if party_time_check():
            if private_party_owner == str(update.message.from_user.id):
                return
            else:
                update.message.forward(chat_id=log_channel)
                bot.send_message(chat_id=log_channel, text="party time")
                update.message.delete()
                return
        else:
            private_party = False
    # permission control
    user_id = update.message.from_user.id
    member = None
    try:
        member = Member.objects.get(t_id=user_id)
    except:
        member = Member.objects.create(t_id=user_id)
        member.add_count = 0
        if update.message.from_user.username is not None:
            update.message.from_user.username = base64.b64encode(update.message.from_user.username.encode())
        if update.message.from_user.first_name is not None:
            update.message.from_user.first_name = base64.b64encode(update.message.from_user.first_name.encode())
        if update.message.from_user.last_name is not None:
            update.message.from_user.last_name = base64.b64encode(update.message.from_user.last_name.encode())
        member.username = update.message.from_user.username
        member.last_name = update.message.from_user.last_name
        member.first_name = update.message.from_user.first_name
        member.permitted_datetime = timezone.now()
        member.save()
    if member.permitted_datetime is None:
        member.permitted_datetime = timezone.now()
        member.save()
    if timezone.now() < member.permitted_datetime:
        pass
    elif member.add_count > 0:
        member.add_count = member.add_count - 1
        member.permitted_datetime = timezone.now() + timezone.timedelta(days=30)
        member.save()
    else:
        m = update.message.forward(chat_id=log_channel)  # type: telegram.Message
        bot.send_message(chat_id=log_channel, text=messageHelper.json["3"].format(update.message.from_user.id,
                                                                                  update.message.from_user.first_name) + "/n" +
                                                   messageHelper.json["22"], reply_to_message_id=m.message_id,
                         parse_mode='HTML')
        update.message.delete()
        return
    post = Post.objects.filter(from_user_id=user_id).filter(datetime__gt=timezone.now() - timezone.timedelta(hours=3))
    if len(post) > 1:
        m = update.message.forward(chat_id=log_channel)
        bot.send_message(chat_id=log_channel, text=messageHelper.json["3"].format(update.message.from_user.id,
                                                                                  update.message.from_user.first_name) + "/n" +
                                                   messageHelper.json["23"], reply_to_message_id=m.message_id,
                         parse_mode='HTML')
        update.message.delete()
        return

    today_min = timezone.datetime.combine(timezone.now().date(), timezone.now().time().min) + timezone.timedelta(
        hours=3)
    today_max = timezone.datetime.combine(timezone.now().date(), timezone.now().time().max) + timezone.timedelta(
        hours=3)
    post = Post.objects.filter(from_user_id=user_id).filter(datetime__range=(today_min, today_max))

    if len(post) > 5:
        m = update.message.forward(chat_id=log_channel)
        bot.send_message(chat_id=log_channel, text=messageHelper.json["24"], reply_to_message_id=m.message_id)
        update.message.delete()
        return

    post = Post.objects.create(msg_id=update.message.message_id)
    post.from_user_id = user_id
    post.datetime = timezone.now()
    post.save()


def manage_new_members_update(bot, update, new_members):
    for m in new_members:  # type: telegram.User
        if m.is_bot:
            bot.kick_chat_member(chat_id=update.message.chat_id, user_id=m.id)
            bot.kick_chat_member(chat_id=update.message.chat_id, user_id=update.message.from_user.id)
            new_members.remove(m)
            return
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
        member.username = base64.b64encode(u.username.encode())
    if u.first_name is not None:
        response = response + u.first_name + ' '
        member.first_name = base64.b64encode(u.first_name.encode())
    if u.last_name is not None:
        response = response + u.last_name
        member.last_name = base64.b64encode(u.last_name.encode())
    response = response + '\n'
    response = response + 'added :\n'
    for m in new_members:  # type: telegram.User
        response = response + str(m.first_name) + '  ' + str(m.last_name) + '  @' + str(m.username) + '\n'
        log = AddLog.objects.create()
        log.log = base64.b64encode(response.encode())
        log.save()
        newM = None
        try:
            newM = Member.objects.get(t_id=m.id)
        except:
            newM = None
        if newM is None:
            member.add_count = member.add_count + 1
            newM = Member.objects.create(t_id=m.id)
            newM.last_name = m.last_name
            newM.first_name = m.first_name
            newM.username = m.username
            newM.add_count = 0
            newM.save()
            channel_log(messageHelper.json["20"].format(messageHelper.json["3"]
                                                        .format(str(member.t_id),
                                                                base64.b64decode(member.first_name).decode())))
        else:
            channel_log(messageHelper.json["21"].format(messageHelper.json["3"]
                                                        .format(str(member.t_id),
                                                                base64.b64decode(member.first_name).decode())))
    member.save()


def channel_text(bot  # type: telegram.Bot
                 , update  # type: telegram.Update
                 ):
    pass


def private_text(bot  # type: telegram.Bot
                 , update  # type: telegram.Update
                 ):
    pass


def reply(bot, update):
    # tries to echo 10 msgs at once
    chatid = update.message.chat_id
    message = update.message  # type: telegram.Message
    bot.send_message(chat_id=chatid,
                     text=messageHelper.json["3"].format(message.from_user.id, "shayan") +
                          " --- " + messageHelper.json["3"].format(nasrinTID, "maman"), parse_mode='HTML')


def cmd_get_user_id(bot  # type: telegram.Bot
                    , update  # type: telegram.Update
                    ):
    bot.send_message(chat_id=update.message.chat_id, text=str(update.message.from_user.id))


def cmd_governor(bot  # type: telegram.Bot
                 , update  # type: telegram.Update
                 , args):
    if update.message.chat.type != telegram.Chat.PRIVATE:
        return
    if not is_master(update.message.from_user.id):
        return
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["0"].format(1))
        return
    cmd = args[0]
    if cmd == "add":
        if len(args) is not 3:
            bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["2"].format("add"))
            return
        id = args[1]
        name = args[2]
        try:
            gov = Governor.objects.get(t_id=id)
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["3"].format(gov.t_id
                                                                 , gov.name) + " - " + str(gov.t_id) +
                                  "\n" + messageHelper.json["6"], parse_mode='HTML')
        except:
            gov = Governor.objects.create(t_id=id)
            gov.name = name
            gov.save()
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["3"].format(gov.t_id
                                                                 , gov.name) + " - " + str(gov.t_id) +
                                  "\n" + messageHelper.json["7"], parse_mode='HTML')
    elif cmd == "remove":
        if len(args) is not 2:
            bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["2"].format("remove"))
            return
        id = args[1]
        try:
            gov = Governor.objects.get(t_id=id)
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["3"].format(gov.t_id, gov.name)
                                  + "\n" + messageHelper.json["9"], parse_mode='HTML')
            gov.delete()
        except:
            bot.send_message(chat_id=update.message.chat_id,
                             text=id + "\n" + messageHelper.json["8"])
    elif cmd == "show":
        governors = Governor.objects.all()
        if governors.__len__() == 0:
            bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["4"])
            return
        text = messageHelper.json["5"]
        for gov in governors:
            text += "\n" + messageHelper.json["3"].format(gov.t_id, gov.name) + " - " + str(gov.t_id)
        bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='HTML')
    else:
        bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["1"])


def cmd_spam(bot  # type: telegram.Bot
             , update  # type: telegram.Update
             , args):
    pass


def delete_all_messages(bot  # type: telegram.Bot
                        , update  # type: telegram.Update
                        ):
    channel_log(messageHelper.json["25"]
                .format(messageHelper.json["3"]
                        .format(update.message.from_user.id
                                , update.message.from_user.first_name)))
    bot.send_message(chat_id=update.message.chat_id,
                     text=messageHelper.json["14"])
    msg = None  # type: telegram.Message

    msg = bot.send_message(chat_id=group, text=messageHelper.json["19"])
    fm = None
    with open("./" + first_message_id_file_name, "r+") as f:
        fm = int(f.readline().__str__())
    for i in range(fm, msg.message_id + 1):
        try:
            bot.delete_message(chat_id=group, message_id=i)
        except telegram.TelegramError as e:
            print(str(i) + "  " + str(e))
    with open("./" + first_message_id_file_name, "w") as f:
        f.write(str(msg.message_id))
    bot.send_message(chat_id=update.message.chat_id,
                     text=messageHelper.json["15"])


def cmd_party(bot  # type: telegram.Bot
              , update  # type: telegram.Update
              , args):
    global private_party
    global private_party_duration
    global private_party_start_time
    global private_party_owner
    global private_party_owner_name
    if update.message.chat.type != telegram.Chat.PRIVATE:
        return
    if not is_governor(update.message.from_user.id):
        return
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id,
                         text=messageHelper.json["0"].format(1))
        return
    cmd = args[0]
    if cmd == "hold":
        if private_party:
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["10"])
            return
        if len(args) != 5:
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["2"].format("hold"))
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["11"].format(5))
            return
        duration = float(args[1])
        owner = args[2]
        owner_name = args[3]
        cost = int(args[4])
        user = None
        try:
            user = Member.objects.get(t_id=owner)
        except:
            user = None
        if user is None:
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["12"].format(owner))
            return
        if user.add_count < cost:
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["13"].format(owner, (cost - user.add_count)))
            return
        delete_all_messages(bot, update)
        private_party_owner = owner
        private_party = True
        private_party_start_time = datetime.datetime.now()
        private_party_duration = duration
        private_party_owner_name = owner_name
        user.add_count = user.add_count - cost
        user.party_count = user.party_count + 1
        user.save()
        channel_log(messageHelper.json["26"].format(
            messageHelper.json["3"].format(update.message.from_user.id, update.message.from_user.first_name)))
        bot.send_message(chat_id=update.message.chat_id,
                         text=messageHelper.json["16"])
        bot.send_message(chat_id=group, text=messageHelper.json["31"]
                         .format(messageHelper.json["3"].format(user.t_id, base64.b64decode(user.first_name).decode()),
                                 str(duration * 60)),
                         parse_mode='HTML')
        return
    elif cmd == "cancel":
        private_party = False
        channel_log(messageHelper.json["27"])
        bot.send_message(chat_id=update.message.chat_id,
                         text=messageHelper.json["16"])
        return
    elif cmd == "show":
        if private_party:
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["17"]
                             .format(int(private_party_duration * 60 -
                                         (datetime.datetime.now()
                                          - private_party_start_time).total_seconds() / 60),
                                     messageHelper.json["3"].format(
                                         private_party_owner
                                         , private_party_owner_name
                                     )), parse_mode='HTML')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text=messageHelper.json["18"])
        return
    else:
        bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["1"])
        return


def cmd_night_time(bot  # type: telegram.Bot
                   , update  # type: telegram.Update
                   ):
    if not is_master(update.message.from_user.id):
        return
    global night_time
    if night_time:
        bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["29"])
        night_time = False
    else:
        bot.send_message(chat_id=update.message.chat_id, text=messageHelper.json["28"])
        night_time = True


def channel_log(text):
    bot.send_message(chat_id=log_channel, text=str(text), parse_mode='HTML')


def cmd_inquiry(bot  # type: telegram.Bot
                , update  # type: telegram.Update
                , args):
    if not is_governor(update.message.from_user.id):
        return
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id,
                         text=messageHelper.json["2"].format("inquiry"))
        return
    id = args[0]
    try:
        m = Member.objects.get(t_id=int(id))
    except:
        bot.send_message(chat_id=update.message.chat_id,
                         text=messageHelper.json["12"].format(id))
        return
    bot.send_message(chat_id=update.message.chat_id,
                     text=messageHelper.json["30"].format(
                         messageHelper.json["3"].format(id, m.first_name), m.add_count
                     ))


def cmd_gm(bot  # type: telegram.Bot
           , update  # type: telegram.Update
           ):
    if not is_master(update.message.from_user.id):
        return
    goodmorning()


def cmd_gn(bot  # type: telegram.Bot
           , update  # type: telegram.Update
           ):
    if not is_master(update.message.from_user.id):
        return
    goodnight()


def cmd_debug(bot  # type: telegram.Bot
              , update  # type: telegram.Update
              ):
    if not is_master(update.message.from_user.id):
        return
    global night_time
    global DEBUG
    global last_night_call
    global last_morning_call
    log = ""
    log += "night_time = " + str(night_time) + "\n"
    log += "debug = " + str(DEBUG) + "\n"
    log += "last_night_call = " + str(last_night_call) + "\n"
    log += "last_morning_call = " + str(last_morning_call) + "\n"

    bot.send_message(chat_id=update.message.chat_id, text=log)


def cmd_restart(bot  # type: telegram.Bot
                , update  # type: telegram.Update
                ):
    if not is_master(update.message.from_user.id):
        return
    bot.send_message(chat_id=update.message.chat_id, text="system rebooted wait for 30 sec")
    import os
    os.system('reboot')


hdl = MessageHandler(Filters.all & (~Filters.command), all_text)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("governor", cmd_governor, pass_args=True)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("id", cmd_get_user_id)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("gm", cmd_gm)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("gn", cmd_gn)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("inquiry", cmd_inquiry, pass_args=True)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("party", cmd_party, pass_args=True)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("nighttime", cmd_night_time)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("deleteallposts", delete_all_messages)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("debug", cmd_debug)
updater.dispatcher.add_handler(hdl)
hdl = CommandHandler("restart", cmd_restart)
updater.dispatcher.add_handler(hdl)

import schedule
import time, _thread


def goodmorning():
    global last_morning_call
    global night_time
    last_morning_call = datetime.datetime.now() + datetime.timedelta(minutes=30)
    night_time = False
    bot.send_sticker(chat_id=group, sticker=goodMorningStickerID)


def goodnight():
    global last_night_call
    global night_time
    last_night_call = datetime.datetime.now() + datetime.timedelta(minutes=30)
    night_time = True
    bot.send_sticker(chat_id=group, sticker=noAdsStickerID)
    bot.send_sticker(chat_id=group, sticker=goodNightStickerID)
    # bot.send_message(chat_id=group, text=buttonManager.staticjson['message_me'])
    # bot.send_message(chat_id=group, text=buttonManager.staticjson['night_time_rule'])


schedule.every().day.at("23:30").do(goodnight)
schedule.every().day.at("05:30").do(goodmorning)


def threadjob():
    while True:
        schedule.run_pending()
        time.sleep(60)


_thread.start_new_thread(threadjob, ())
updater.start_polling()


# template
def methodName(bot  # type: telegram.Bot
               , update  # type: telegram.Update
               , args):
    pass
