from django.db import models
from django.utils import timezone


# Create your models here.


class Member(models.Model):
    t_id = models.BigIntegerField(unique=True, null=False, blank=False)
    add_count = models.IntegerField(null=True, blank=True, )
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_message_date = models.DateTimeField(null=True, blank=True)
    chat_id = models.BigIntegerField(blank=True, null=True, default=0)
    party_count = models.IntegerField(default=0)
    permitted_datetime = models.DateTimeField(null=True)
    first_error = models.BooleanField(default=False)

    def __str__(self):
        return str(self.t_id)


class Spam(models.Model):
    word = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.word


class AddLog(models.Model):
    log = models.CharField(max_length=2500, null=True)

    def __str__(self):
        return self.log


class BotAdmin(models.Model):
    t_id = models.BigIntegerField(unique=True, null=False, blank=False)

    def __str__(self):
        return self.t_id


class Governor(models.Model):
    t_id = models.BigIntegerField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, default="")

    def __str__(self):
        return str(self.t_id)


class Post(models.Model):
    msg_id = models.BigIntegerField(unique=True, null=False, blank=False)
    datetime = models.DateTimeField(null=True,blank=True)
    from_user_id = models.BigIntegerField(null=True,blank=True)
