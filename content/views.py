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

CONTENT = "/content/"


def content(request, section):

    (body, mtime) = _get_page(section, "index.html")
    context = {
        'page_image': "",
        'page_title': "",
        'page_description': "",
        'section': section,
        'home': CONTENT,
        'body': body,
        'mtime': mtime,
        'server': WEBROOT,
        'staticServer': WEBROOT,
        'intro': "",
        'feedback': "{}@nosher.net".format(section),
    }
    return render(request, 'content/page.html', context)


def content_page(request, section, page):

    (body, mtime) = _get_page(section, page)
    context = {
        'page_image': "",
        'page_title': "",
        'page_description': "",
        'section': section,
        'home': CONTENT,
        'body': body,
        'mtime': mtime,
        'server': WEBROOT,
        'staticServer': WEBROOT,
        'intro': "",
        'feedback': "{}@nosher.net".format(section),
    }
    return render(request, 'content/page.html', context)


def _get_page(section, page):
    path = "/home/httpd/nosher.net/docs/content/{}/{}".format(section, page)
    mtime = datetime.date.fromtimestamp(os.stat(path)[7])
    with open(path, encoding="utf-8") as fh:
        body = _format_page(section, fh.read())
        t = Template(body)
        return (t.render(Context({'staticServer': WEBROOT})), mtime)
        

def _format_page(section, page):

    lines = page.split("\n")
    newlines = []
    script = False
    for l in lines:
        if l != "":
            if l.find("[picture") > -1:
                groups = re.findall("\[picture: (?P<pic>.*?)\]", l, re.S|re.MULTILINE)
                if not groups is None:
                    for pic in groups:
                        repl = "[picture: %s]" % pic
                        bits = pic.split("|")
                        target = """<div class="grid1"><img class="ctrimg" src="https://static.nosher.net/content/{}/images/{}" alt="{}" title="{}"><p class="desc">{}</p></div>""".format(section, bits[0], bits[1], bits[1], bits[1])
                        newlines.append(l.replace(repl, target))
            elif l[0] == "~":
                newlines.append("""<blockquote class="ref">{}</blockquote>\n""".format(l[1:]))
            elif l.strip()[:7] == "<script" or l[:8] == "[recipe]":
                script = True
                newlines.append(l + "\n") 
            elif l.strip()[:8] == "</script" or l[:5] == "[end]":
                script = False
                newlines.append(l + "\n") 
            elif l.strip()[:1] != "<" and l != "" and not script:
                newlines.append("\n<p>{}</p>".format(l))
            else:
                newlines.append(l + "\n")

    page = "".join(newlines)

    # resolve any custom tags in content, e.g. for recipes
    if page.find("[recipe]") > -1:
        (start, rest) = page.split("[recipe]")
        (recipe, rest) = rest.split("[end]")
        parts = recipe.split("--") # intro, recipe, method, serve
        if len(parts) > 3:
            imgmatch = '\|(.*?)\|'
            method = "<ol>\n"
            exc_empty = lambda item: item != ""
            recipe = parts[1].split("\n")
            filtered_recipe = filter(exc_empty, recipe)
            steps = parts[2].split("\n")
            filtered_steps = filter(exc_empty, steps)
            for step in filtered_steps:
                imgs = re.search(imgmatch, step)
                if imgs is not None:
                    img = imgs.group().replace("|", "")
                    tag = """<br /><img class="recimg" src="{}/content/recipes/images/{}.jpg" /><br />""".format(WEBROOT, img)
                    step = step.replace(imgs.group(), tag)
                method = method + "<li>{}</li>\n".format(step) 
            method = method + "</ol>"
            extras = ""
            if len(parts) > 4 and parts[4].strip() != "":
                extras = "\n<diet->Healthier variation: {}".format(parts[4])
            return """<p><a href="/content/recipes/" class="dots">Recipe index</a></p>{}\n<intro->{}</intro->\n<recipe->{}</recipe->\n<method->\n{}\n</method->\n<serve->{}</serve->\n{}\n{}"""\
                .format(start, parts[0], "\n".join(filtered_recipe), method, parts[3], rest, extras)
    else:
        groups = re.findall("\[picture: (?P<pic>.*?)\]", page, re.S|re.MULTILINE)
        if not groups is None:
            for pic in groups:
                repl = "[picture: %s]" % pic
                bits = pic.split("|")
                target = """<div class="grid1"><img class="ctrimg" src="https://static.nosher.net/content/raf69th/images/{}" alt="{}" title="{}"><p class="desc">{}</p></div>""" \
                    .format(bits[0], bits[1], bits[1], bits[1])
                page = page.replace(repl, target)
        return page
