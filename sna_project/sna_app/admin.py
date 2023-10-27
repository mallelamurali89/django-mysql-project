from django.contrib import admin
from .models import FriendRequest

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')

admin.site.register(FriendRequest, FriendRequestAdmin)
