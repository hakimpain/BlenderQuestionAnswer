


from django.urls import path
from . import views

urlpatterns = [
    path('',views.version_request,name='version_request'),
    path('request_version_vdb/',views.request_version_vdb,name='request_version_vdb'),

]