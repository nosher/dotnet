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

from whoosh.index import open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser


CONTENT = "/content/"

@register.filter(name='split')
def split(value, arg):
    return value.split(',')

def search(request):

    ix = open_dir("/home/httpd/django/nosher/index")
    query = request.GET["q"]
    off = int(request.GET.get("o", "0"))
    qp = QueryParser("content", schema = ix.schema)
    q = qp.parse(query)
    results =[] 
    start = 0
    page = 50
    with ix.searcher() as s:
        results = s.search(q, limit = 500, sortedby="date", reverse=True)
        existing = []
        filtered = []
        pparams = []
        nparams = []
        for res in results:
            if not res["path"] in existing:
                filtered.append(res)
                existing.append(res["path"])
        if start + page < len(filtered):
            end = len(filtered) - start
            nparams.extend(["q={}".format(query), "o={}".format(start + page)])
        else:
            end = start + page
            nxt  = end
        if off > 0:
            pparams.extend(["q={}".format(query), "o={}".format(off - page)])
        else:
            prev = 0
        context = {
            'query': query,
            'results': filtered[start:end],
            'next': None if len(nparams) == 0 else "/search?" + "&".join(nparams),
            'prev': None if len(pparams) == 0 else "/search?" + "&".join(pparams),
            'page': page,
            'server': WEBROOT,
        }
        return render(request, 'search/search.html', context)


