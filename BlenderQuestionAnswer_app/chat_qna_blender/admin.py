from django.contrib import admin

from .models import ChatMessage,ChatSession

admin.site.register(ChatMessage)
admin.site.register(ChatSession)
# Register your models here.
