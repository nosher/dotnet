from django.shortcuts import render
from django.http import HttpResponse
from ..images.models import PhotoAlbum

from datetime import datetime
from datetime import date
from django.template.defaulttags import register

@register.filter
def get_now(null):
    return date.today().year

def index(request):

    latest_albums = PhotoAlbum.objects.order_by('-date_created')[:6]
    context = {
        'latest_albums': latest_albums,
    }
    return render(request, 'home/index.html', context)
