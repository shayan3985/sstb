from django.contrib import admin
from .models import Member , Spam , AddLog , BotAdmin
# Register your models here.

admin.site.register(Member)
admin.site.register(Spam)
admin.site.register(AddLog)
admin.site.register(BotAdmin)