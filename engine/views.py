from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    message = "Salut tout le monde !"
    return HttpResponse(message)