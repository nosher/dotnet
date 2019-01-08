import os
import re
import locale
import sys

from django.template import Template
from django.template import Context, loader
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import ordinal
from django.db.models import Count
from stat import *
from datetime import datetime
from datetime import date
from .constants import *
from collections import OrderedDict

CONTENT = "/content/"


def content(request, section):

    body = _get_page(section, "index.html")
    context = {
        'page_image': "",
        'page_title': "",
        'page_description': "",
        'home': CONTENT,
        'body': body,
        'intro': "",
    }
    return render(request, 'content/page.html', context)


def content_page(request, section, page):

    body = _get_page(section, page)
    context = {
        'page_image': "",
        'page_title': "",
        'page_description': "",
        'home': CONTENT,
        'body': body,
        'intro': "",
    }
    return render(request, 'content/page.html', context)

def _get_page(section, page):
    with open("/home/httpd/nosher.net/docs/content/{}/{}".format(section, page)) as fh:
        body = fh.read()
        t = Template(body)
        return t.render(Context({'staticServer': WEBROOT}))
        
