import os

from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from .models import PhotoAlbum
from .models import PhotoAlbums

from stat import *
from datetime import datetime

from ..constants import * 

DOCROOT = "images"
ROOT = "/home/httpd/nosher.net/docs/" + DOCROOT

def index(request):
    latest_albums = PhotoAlbum.objects.order_by('-date_created')[:30]
    context = {
        'latest_albums': latest_albums,
        'years': _getYears()
    }
    return render(request, 'images/index.html', context)


def year(request, album_year):
    albums = PhotoAlbum.objects.filter(year=album_year).order_by('-path')
    context = {
        'year': album_year,
        'albums': albums,
        'years': _getYears(),
    }
    return render(request, 'images/year.html', context)


def album(request, album_year, album_path, index=-1):
    try:
        album = PhotoAlbum.objects.get(path="{}/{}".format(album_year, album_path))
    except PhotoAlbum.DoesNotExist:
        raise Http404("Album does not exist")

    # get all albums and find next and previous
    all_albums = PhotoAlbum.objects.order_by('path')
    prv = nxt = None 
    for i in range(len(all_albums)):
        if all_albums[i].path == album_year + "/" + album_path:
            if i > 0:
                prv = all_albums[i - 1]
            if i < len(all_albums) - 1:
                nxt = all_albums[i + 1]
    (title, intro, images, mtime) = _getAlbumDetails("{}/{}".format(album_year, album_path))
    fmt_date = datetime.fromtimestamp(mtime).strftime("%d %B %Y")
    context = {
        'path': album_path,
        'year': album_year,
        'album': album,
        'title': title,
        'intro': intro,
        'images': images,
        'mtime': fmt_date,
        'years': _getYears(),
        'index': index,
        'next': nxt,
        'prev': prv,
        'url': "{}/{}/{}/{}".format(WEBROOT, DOCROOT, album_year, album_path)
    }
    return render(request, 'images/album.html', context)


def _getAlbumDetails(album_path):
    path = os.path.join(ROOT, album_path, "details.txt")
    with open(path) as fh:
        items = []
        title = ""
        intro = ""
        stats = os.stat(path)
        for line in fh.readlines():
            line = line.replace("\n", "")
            parts = line.split("\t")
            if parts[0] == "title":
                title = parts[1]
            elif parts[0] == "intro":
                intro = parts[1]
            elif parts[0] == "locn":
                pass
            else:
                items.append({"thumb": parts[0], "caption": parts[1].replace("\"","\'")})
                
        return (title, intro, items, stats[ST_MTIME]) 

def _getYears():
    years = PhotoAlbums.objects.order_by('xorder', '-year')
    for year in years:
        count = PhotoAlbum.objects.filter(year=year.year).count()
        year.setCount(count)
    return years
    
