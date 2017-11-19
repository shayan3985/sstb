from button import Button, Method
import telegram
from database.models import Member

buttonManager = Button()

class MenuHandler:


    def help(self , bot  # type: telegram.Bot
             , update  # type: telegram.Update
             , cq  # type: telegram.CallbackQuery
             ):
        cq.edit_message_text(text=str(buttonManager.staticjson['helpText'])
                             , reply_markup=buttonManager.generateReturnMarkUp())


    def mainMenu(self,bot  # type: telegram.Bot
             , update  # type: telegram.Update
             , cq  # type: telegram.CallbackQuery
             ):
        cq.edit_message_text(text=str(buttonManager.staticjson['mainMenuText'])
                             , reply_markup=buttonManager.generateMainMenuMarkUp())

    def showToken(self,bot  # type: telegram.Bot
             , update  # type: telegram.Update
             , cq  # type: telegram.CallbackQuery
             ):
        member = None
        m = cq.message #type: telegram.Message
        try:
            member = Member.objects.get(t_id=cq.from_user.id)
        except:
            member = Member.objects.create(t_id=cq.from_user.id)
            member.add_count = 0

        if cq.from_user.username is not None:
            member.username = cq.from_user.username
        if cq.from_user.first_name is not None:
            member.first_name = cq.from_user.first_name
        if cq.from_user.last_name is not None:
            member.last_name = cq.from_user.last_name
        member.save()
        response = 'you have ' + str(int(member.add_count )) + ' token'
        cq.edit_message_text(text = response,reply_markup = buttonManager.generateReturnMarkUp())

