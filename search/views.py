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
from ..constants import *
from collections import OrderedDict

from whoosh.index import open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.query import Query
from whoosh import query


CONTENT = "/content/"

@register.filter(name='split')
def split(value, arg):
    return value.split(',')


@register.filter(name='ellipsize')
def _format_content(content):
    return _get_ellipsis(content, 36, 30)


@register.filter(name='details')
def _create_tooltip(result):
    path = result["path"]
    parts = path.split("/")
    year = ""
    if parts[0] == "images":
        year = "{}: ".format(parts[1])
    return "{}{}".format(year, _get_ellipsis(result["content"], 1206, 110))


def search(request):

    ix = open_dir("/home/httpd/django/nosher/index")
    query_param = request.GET["q"]
    q_filter = request.GET.get("filter", "")
    start = int(request.GET.get("o", "0"))
    qp = QueryParser("content", schema = ix.schema)
    q = qp.parse(query_param)
    results =[] 
    page = 50
    restrict_q = None
    if q_filter == "photos":
        restrict_q = query.Term("path", "images/")
    elif q_filter == "micros":
        restrict_q = query.Term("path", "computers/")

    with ix.searcher() as s:
        if restrict_q:
            results = s.search(q, limit = 500, sortedby="date", reverse=True, mask=restrict_q)
        else:
            results = s.search(q, limit = 500, sortedby="date", reverse=True)
        existing = []
        filtered = []
        pparams = []
        nparams = []
        for res in results:
            if not res["path"] in existing:
                filtered.append(res)
                existing.append(res["path"])
        if start + page > len(filtered) or len(filtered) - start - page < 10:
            end = len(filtered)
        else:
            end = start + page
            nxt = end
            nparams.extend(["q={}".format(query_param), "o={}".format(end)])
        if start > 0:
            pparams.extend(["q={}".format(query_param), "o={}".format(start - page)])
        else:
            prev = 0
        context = {
            'query': query_param,
            'start': start,
            'end': end,
            'total': len(filtered),
            'results': map(_format_content, filtered[start:end]),
            'next': _get_url(nparams),
            'prev': _get_url(pparams),
            'page': page,
            'server': WEBROOT,
        }
        return render(request, 'search/search.html', context)


def _get_ellipsis(content, longlen, shortlen):
    if len(content) < longlen:
        return content
    else:
        words = content.replace("-", " ").split(" ")
        length = 0
        w = 0
        while length < shortlen and w < len(words) - 1:
            length += len(words[w])
            w += 1
        return " ".join(words[0:w]) + " " + re.sub(r'[ ,.:-]', '', words[w]) + "..."


def _get_url(params):
    return None if len(params) == 0 else "/search?" + "&".join(params)
