from django.contrib import admin
from .models import Member, Spam, AddLog, BotAdmin, Governor, Post


# Register your models here.

class CustomerMember(admin.ModelAdmin):
    # The forms to add and change user instances
    # form = CustomerChangeForm
    # add_form = CustomerCreationForm

    # def get_form(self, request, obj=None, **kwargs):
    #     # Proper kwargs are form, fields, exclude, formfield_callback
    #     if obj:
    #         self.form = CustomerChangeForm
    #     else:
    #         self.form = CustomerCreationForm
    #     return super(CustomerAdmin, self).get_form(request, obj, **kwargs)

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    model = Member
    # list_display = ( 'username','first_name', 'last_name','first_time',)
    # list_filter = ('last_name',)
    # fieldsets = (
    #     (None, {'fields': ('username', 'password')}),
    #     ('Personal info', {'fields': ('first_name','last_name','phone'
    #                                   ,)}),
    #     ('Permissions', {'fields': ('is_admin','special_user','is_active',)}),
    #
    # )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('username', 'first_name','last_name','phone', 'password1', 'password2')}
    #     ),
    #
    # )

    search_fields = ('t_id',)
    filter_horizontal = ()


admin.site.register(Member)#, CustomerMember)
admin.site.register(Spam)
admin.site.register(AddLog)
admin.site.register(BotAdmin)
admin.site.register(Governor)
admin.site.register(Post)
