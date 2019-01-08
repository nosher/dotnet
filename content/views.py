import os
import re
import locale
import sys
import datetime

from stat import *

from django.template import Template
from django.template import Context, loader
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import ordinal
from django.db.models import Count
from stat import *
from .constants import *
from collections import OrderedDict

CONTENT = "/content/"


def content(request, section):

    (body, mtime) = _get_page(section, "index.html")
    context = {
        'page_image': "",
        'page_title': "",
        'page_description': "",
        'home': CONTENT,
        'body': body,
        'mtime': mtime,
        'intro': "",
    }
    return render(request, 'content/page.html', context)


def content_page(request, section, page):

    (body, mtime) = _get_page(section, page)
    context = {
        'page_image': "",
        'page_title': "",
        'page_description': "",
        'home': CONTENT,
        'body': body,
        'mtime': mtime,
        'intro': "",
    }
    return render(request, 'content/page.html', context)

def _get_page(section, page):
    path = "/home/httpd/nosher.net/docs/content/{}/{}".format(section, page)
    mtime = datetime.date.fromtimestamp(os.stat(path)[7])
    with open(path) as fh:
        body = fh.read()
        t = Template(body)
        return (t.render(Context({'staticServer': WEBROOT})), mtime)
        
