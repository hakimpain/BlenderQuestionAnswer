

from django.urls import path
from . import views

urlpatterns = [
    path('get_answer/',views.get_answer,name='get_answer'),
    path('load_chat_history/<str:version>/',views.load_chat_history,name='load_chat_history'),
    path('clean_chat_history/',views.clean_chat_history,name='clean_chat_history')

]