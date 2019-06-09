import os

from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.db.models import Q
from .models import PhotoAlbum
from .models import PhotoAlbums

from stat import *
from datetime import datetime

from ..constants import * 

DOCROOT = "images"
ROOT = "/home/httpd/nosher.net/docs/" + DOCROOT

def index(request):
    params = request.GET
    if "group" in params:
        keys = params.get("group").split(",")
        title = params.get("title")
        if len(keys) == 1:
            albums = PhotoAlbum.objects.filter(title__contains = keys[0]).order_by('-path')
        else:
            q = Q(title__contains = keys[0])
            for i in range(1, len(keys)):
                q |= Q(title__contains = keys[i])
            albums = PhotoAlbum.objects.filter(q).order_by('-path')
        context = {
            'years': _getYears(),
            'albums': albums,
            'title': title,
            'groups': _getGroups()
        }
        return render(request, 'images/groups.html', context)
    else:
        latest_albums = PhotoAlbum.objects.order_by('-date_created')[:30]
        context = {
            'latest_albums': latest_albums,
            'years': _getYears(),
            'intro': _getTextForAlbum(ROOT),
            'groups': _getGroups()
        }
        return render(request, 'images/index.html', context)


def year(request, album_year):
    albums = PhotoAlbum.objects.filter(year=album_year).order_by('-path')
    context = {
        'year': album_year,
        'albums': albums,
        'years': _getYears(),
        'groups': _getGroups(),
        'intro': _getTextForAlbum(os.path.join(ROOT, album_year))
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
        'groups': _getGroups(),
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

    
def _getTextForAlbum(path):
    file_path = os.path.join(path, "intro.txt")
    try:
        with open(file_path) as fh:
            return fh.read()
    except IOError:
        return ""


def _getGroups():
    with open(os.path.join(ROOT, "filters.txt")) as fh:
        groups = fh.readlines()
        group_list = [] 
        for group in groups:
            (title, keys) = group.split("|")
            group_list.append({"title": title, "keys": keys.rstrip("\n")})

        return group_list
    return None

