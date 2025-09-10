

from django.http import HttpResponse
from django.shortcuts import render
from version_request_vdb.utils import get_available_versions

def home(request):
    return render(request,'home.html',{'available_versions':get_available_versions()})