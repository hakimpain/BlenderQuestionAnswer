from django.db import models
from accounts.models import User
# Create your models here.

class ChatSession(models.Model):
    version = models.CharField(max_length=4,unique=True,primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.version

class ChatMessage(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    chat_session = models.ForeignKey(ChatSession,on_delete=models.CASCADE)

    question = models.CharField(max_length=2000)
    answer = models.CharField(max_length=5000)
    suggestion = models.CharField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_data_for_history(self):
        return {
            'question':self.question,
            'answer':self.answer,
            'suggestions':self.suggestion
        }