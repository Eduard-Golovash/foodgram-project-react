from django.shortcuts import render
from django.http import HttpResponse

def dummy_view(request):
    return HttpResponse("This is a dummy view.")
