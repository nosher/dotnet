import os

from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.db.models import Q
from .models import PhotoAlbum
from .models import PhotoAlbums

from stat import *
import datetime

from ..constants import * 

DOCROOT = "images"
ROOT = "/home/httpd/nosher.net/docs/" + DOCROOT
EMAIL = "photos@nosher.net"

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
            'staticServer': WEBROOT,
            'feedback': EMAIL,
            'groups': _getGroups()
        }
        return render(request, 'images/groups.html', context)
    else:
        latest_albums = PhotoAlbum.objects.order_by('-date_created')[:40]
        context = {
            'latest_albums': latest_albums,
            'years': _getYears(),
            'intro': _getTextForAlbum(ROOT),
            'staticServer': WEBROOT,
            'feedback': EMAIL,
            'groups': _getGroups()
        }
        return render(request, 'images/index.html', context)


def nojs(request):
    params = request.GET
    year = path = thumb = None
    if "year" in params:
        year = params.get("year")
    if "path" in params:
        path = params.get("path")
    if "thumb" in params:
        thumb = int(params.get("thumb"))
    (title, intro, images, mtime, dimensions, webp) = _getAlbumDetails("{}/{}".format(year, path))
    img = images[thumb]
    context = {
        'year': year,
        'path': path,
        'title': title,
        'page_title': title,
        'webp_source': webp,
        'album': "/images/{}/{}".format(year, path),
        'page_description': img["caption"],
        'page_image': "{}/{}/{}/{}/{}{}".format(WEBROOT, DOCROOT, year, path, img["thumb"], "-m.jpg"),
        'staticServer': WEBROOT,
        'page_url': "{}/{}/{}/{}/{}".format("https://nosher.net", DOCROOT, year, path, thumb),
        'img': img
    }
    return render(request, 'images/nojs.html', context)


def year(request, album_year):
    albums = PhotoAlbum.objects.filter(year=album_year).order_by('-path')
    context = {
        'year': album_year,
        'albums': albums,
        'years': _getYears(),
        'staticServer': WEBROOT,
        'groups': _getGroups(),
            'feedback': EMAIL,
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
    (title, intro, images, mtime, dimensions, webp) = _getAlbumDetails("{}/{}".format(album_year, album_path))
    spotify = _getSpotifyDetails("{}/{}".format(album_year, album_path))
    fmt_date = datetime.datetime.fromtimestamp(mtime).strftime("%d %B %Y")
    if request.META["HTTP_ACCEPT"].find("image/webp") > -1:
        accept_webp = "true" 
    else:
        accept_webp = "false"

    context = {
        'path': album_path,
        'year': album_year,
        'album': album,
        'title': title,
        'page_title': title,
        'intro': intro,
        'page_description': intro,
        'page_image': "{}/{}/{}/{}/{}{}".format(WEBROOT, DOCROOT,album_year,  album_path, images[0]["thumb"], "-m.jpg"),
        'images': images,
        'mtime': fmt_date,
        'dimensions': dimensions,
        'staticServer': WEBROOT,
        'accept_webp': accept_webp,
        'is_webp': webp,
        'years': _getYears(),
        'groups': _getGroups(),
        'index': index,
        'spotify': spotify,
        'next': nxt,
        'prev': prv,
        'feedback': EMAIL,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'page_url': "{}/{}/{}/{}".format("https://nosher.net", DOCROOT, album_year, album_path)
    }
    return render(request, 'images/album.html', context)


def _getSpotifyDetails(album_path):
    path = os.path.join(ROOT, album_path, "song.txt")
    try:
        with open(path, encoding="utf-8") as fh:
            # example: https://open.spotify.com/track/2GF0D3d6LKIsDnk8ufpBQa
            url = fh.readlines()[0]
            return "/".join(url.split("/")[-2:])
    except Exception:
        return None


def _getAlbumDetails(album_path):
    path = os.path.join(ROOT, album_path, "details.txt")
    dimensions = os.path.join(ROOT, album_path, "dimensions.txt")
    dims = [] 

    # get image dimensions, if available
    try: 
        with open(dimensions, encoding="utf-8") as d:
            for d in d.readlines():
                d = d.replace("\n", "")
                (name, ratio) = d.split("\t")
                dims.append({"name": name, "ratio": ratio})
    except Exception:
        pass # no dimensions

    # get album details
    with open(path, encoding="utf-8") as fh:
        items = []
        title = ""
        intro = ""
        stats = os.stat(path)
        for line in fh.readlines():
            if not line[0:1] == "#":
                line = line.replace("\n", "")
                parts = line.split("\t")
                if parts[0] == "title":
                    title = parts[1]
                elif parts[0] == "intro":
                    intro = parts[1]
                elif parts[0] == "locn":
                    pass
                else:
                    path = parts[0]
                    if path.find("/") < 0:
                        path = "{}/{}".format(album_path, parts[0])
                    items.append({"thumb": path, "id": parts[0], "caption": parts[1].replace("\"","\'"), "height": 0})
        f1 = items[0]["thumb"]
        if os.path.exists(os.path.join(ROOT, "{}-m.webp".format(f1))):
            webp_source = "true"
        else :
            webp_source = "false"
        return (title, intro, items, stats[ST_MTIME], dims, webp_source) 


def _getYears():
    years = PhotoAlbums.objects.order_by('xorder', '-year')
    cut_off = datetime.datetime.now() - datetime.timedelta(days=60)
    clip = cut_off.strftime("%Y-%m-%d")
    for year in years:
        new_albums = PhotoAlbum.objects.filter(year=year.year).filter(date_created__gte=clip).count()
        year.setHasNew(new_albums > 0)
    return years

    
def _getTextForAlbum(path):
    file_path = os.path.join(path, "intro.txt")
    try:
        with open(file_path, encoding="utf-8") as fh:
            return fh.read()
    except IOError:
        return ""


def _getGroups():
    with open(os.path.join(ROOT, "filters.txt"), encoding="utf-8") as fh:
        groups = fh.readlines()
        group_list = [] 
        for group in groups:
            (title, keys) = group.split("|")
            group_list.append({"title": title, "keys": keys.rstrip("\n")})

        return group_list
    return None

def api_latest(request):
    latest = PhotoAlbum.objects.order_by('-date_created')[:30]
    output = []
    for album in latest:
        (title, intro, items, stats, dimensions, webp) = _getAlbumDetails(album.path)    
        output.append("""{{"path":"{}", "title": "{}", "thumb": "{}"}}""".format(album.path, album.title.replace("\"", "'"), items[1]["thumb"]))
    context = {
        'body': """{{"latest": [{}]}}""".format(", ".join(output)),
        'staticServer': WEBROOT,
    }
    response = render(request, 'images/api.html', context, content_type="text/plain; charset=UTF-8")
    return HttpResponse(response, content_type="text/plain; charset=UTF-8")

def api_years(request):
    years = _getYears()
    output = []
    for year in years:
        output.append("""{{"year":"{}", "count": {}, "new": "{}"}}""".format(
            year.year, year.getCount(), year.hasNew))
    context = {
        'body': """[{}]""".format(", ".join(output)),
        'staticServer': WEBROOT,
    }
    response = render(request, 'images/api.html', context, content_type="text/plain; charset=UTF-8")
    return HttpResponse(response, content_type="text/plain; charset=UTF-8")

def api_year(request, album_year):
    albums = PhotoAlbum.objects.filter(year=album_year).order_by('-path')
    output = []
    for album in albums:
        (title, intro, items, stats, dimensions, webp) = _getAlbumDetails(album.path)    
        output.append("""{{"path":"{}", "title":"{}", "thumb": "{}"}}""".format(album.path, album.title.replace("\n", "").replace("\"", "'"), items[1]["thumb"]))
    context = {
        'body': """{{"year": [{}]}}""".format(", ".join(output)),
        'staticServer': WEBROOT,
    }
    response = render(request, 'images/api.html', context, content_type="text/plain; charset=UTF-8")
    return HttpResponse(response, content_type="text/plain; charset=UTF-8")

def api_album(request, album_year, album_path):
    
    (title, intro, items, modified, dimensions, webp) = _getAlbumDetails(album_year + "/" + album_path)
    output = []
    for item in items:
        output.append("""{{"thumb": "{}", "caption": "{}"}}""".format(item["thumb"], item["caption"].replace("\"", "'")))
    context = {
        'body': """{{"title": "{}", "intro": "{}", "modified": "{}", "items": [{}]}}""".format(title.replace("\"", "'"), intro.replace("\"", "'"), modified, ", ".join(output)),
        'staticServer': WEBROOT,
    }
    response = render(request, 'images/api.html', context, content_type="text/plain; charset=UTF-8")
    return HttpResponse(response, content_type="text/plain; charset=UTF-8")
