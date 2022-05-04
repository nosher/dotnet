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
    
    now = datetime.now()
    clip = now.strftime("-%m-")
    this_month = PhotoAlbum.objects.filter(path__contains=clip)[:30]
    latest_albums = PhotoAlbum.objects.order_by('-date_created')[:6]
    this_day = []
    for latest in this_month:
        path = latest.path
        try:
            with open("/home/httpd/nosher.net/docs/images/{}/details.txt".format(path)) as fh:
                lines = fh.readlines()
                bits = lines[3].split("\t")
                if (len(bits) > 1):
                    this_day.append(("{}/{}-s.jpg".format(path, bits[0]), path))
        except Exception:
            pass
            
    #for album in latest_albums:
    #    path = album.path
    #    with open("/home/httpd/nosher.net/docs/images/{}")
    
    splash = [1,2,4,5,6,7,8,9]
    pic_url = "https://static.nosher.net/graphics/v3/splash{}.jpg".format(splash[random.randint(0, len(splash) - 1)])
    context = {
        'WEBROOT': WEBROOT,
        'this_month': this_day[0:24],
        'latest_albums': latest_albums,
        'random_photo': pic_url,
        'staticServer': WEBROOT,
    }
    return render(request, 'home/index.html', context)
