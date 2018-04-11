from django.contrib import admin
from .models import MyUser, UserOTP, Trading_Platform
from django.contrib.auth.models import Group

# Register your models here.
@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'email']

admin.site.unregister(Group)
admin.site.register(Trading_Platform)