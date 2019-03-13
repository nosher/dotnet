import random

from django.shortcuts import render
from django.http import HttpResponse
from ..images.models import PhotoAlbum
from ..constants import *

from datetime import datetime
from datetime import date
from django.template.defaulttags import register

@register.filter
def get_now(null):
    return date.today().year

def index(request):

    latest_albums = PhotoAlbum.objects.order_by('-date_created')[:6]
    #for album in latest_albums:
    #    path = album.path
    #    with open("/home/httpd/nosher.net/docs/images/{}")
    
    splash = [1,2,4,5,6,7,8,9]
    pic_url = "https://static.nosher.net/graphics/v3/splash{}.jpg".format(splash[random.randint(0, len(splash) - 1)])
    context = {
        'WEBROOT': WEBROOT,
        'latest_albums': latest_albums,
        'random_photo': pic_url,
    }
    return render(request, 'home/index.html', context)
