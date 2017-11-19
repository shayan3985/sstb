from telegram import InlineKeyboardMarkup , InlineKeyboardButton , ReplyKeyboardMarkup
import json

class Button:
    def __init__(self):
        with open('staticjson' , 'r' ) as f:
            self.staticjson = json.loads(f.read())

    def generateMainMenuMarkUp(self):
        button_list = [
            InlineKeyboardButton(self.staticjson['help'], callback_data = str(Method.button_help)),
            InlineKeyboardButton(self.staticjson['showToken'], callback_data= str(Method.button_show_token)),
            InlineKeyboardButton(self.staticjson['newAd'], callback_data=str(Method.button_new_ad))
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
        return reply_markup

    def generateReturnMarkUp(self):
        button_list = [
            InlineKeyboardButton(self.staticjson['return'], callback_data=str(Method.button_return)),
        ]
        return InlineKeyboardMarkup(build_menu(button_list,n_cols=1))


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

class Method:
    button_new_ad = 0
    button_help = 1
    button_plus = 2
    button_minus = 3
    button_show_token = 4
    button_cancel = 5
    button_return = 6
