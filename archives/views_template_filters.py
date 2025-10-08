import re
import locale
import sys

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import ordinal

from stat import *
from datetime import datetime
from .models import ArchiveItems
from ..constants import *
from datetime import date
from datetime import datetime

from .views_filters import *
from .views_advert import *

ARCHIVES = "/archives/computers"
ARCHIVEROOT = "/home/httpd/nosher.net/docs" + ARCHIVES
EMAIL = "microhistory@nosher.net"

def convert_to_text(body):
          
    char_limit = 180 
    body = list(filter(lambda s: s[0] is not "-", body))
    # convert acronyms and values
    raw_body = " ".join(convert_values(convert_acronyms(body))).replace("\n", "")
    # remove wiki-like tags
    raw_body = re.sub("\[.*?\]", "", raw_body)
    # remove HTML
    raw_body = re.sub("<.*?>", "", raw_body)
    # limit to 300 chars
    ellipsis = "..." if len(raw_body) > char_limit else ""
    raw_body = (raw_body[:char_limit] + ellipsis).strip()
    return raw_body


@register.filter
def get_item(dictionary, key):
    item = "".join(convert_values([dictionary.get(key)]))
    item = re.sub(CLEANER, "", item)
    if len(item) < CHARS:
        return item
    else:
        return item[0:CHARS] + "..."


@register.filter
def get_now(null):
    return date.today().year


@register.filter
def get_year(raw_year):
    if raw_year == "":
        return "Unknown"
    parts = list(map(lambda x: int(x), raw_year.split("-")))
    if parts[1] == 0:
        return "{}".format(parts[0])
    if len(parts) < 3 or parts[2] == 0:
        dt = datetime(parts[0], parts[1], 1, 0, 0)
        return dt.strftime('%B %Y')
    else:
        dt = datetime(parts[0], parts[1], 1, 0, 0)
        return "{} {}".format(ordinal(parts[2]), dt.strftime('%B %Y'))

@register.filter
def get_year_only(raw_year):
    if raw_year == "":
        return "Unknown"
    parts = list(map(lambda x: int(x), raw_year.split("-")))
    return parts[0]


@register.filter
def get_first_image(adid):
    return adid.split(",")[0]


@register.filter
def encodeslash(url):
    """
    used to convert model names with a slash, e.g. DB 8/1 or CP/M, to something that doesn't look like a 
    URL boundary. Unfortunately, urlencode doesn't work because Django decodes the URL before it
    passes it through the urlconf pattern matcher, hence we get /computers/model/CP/M
    """
    return url.replace("/", "|")


@register.filter
def get_first_advert(company):
    """
    get the first advert for a company - used primary as a shortcut to find the adid for companies
    which have only a single advert, so we show that instead of a company list
    """
    item = ArchiveItems.objects.filter(company=company)[0]
    return item.adid


def convert_values(item):
    """ 
    Convert occurances of [[123|1983]] to current value based
    upon the Retail Price Index over the intervening years
    """
    locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
    for i in range(len(item)):
            groups = re.findall("\[\[(?P<val>[0-9]+?)\|(?P<year>[0-9]+?)\]\]", item[i], re.S|re.MULTILINE|re.IGNORECASE)
            if not groups is None:
                for group in groups:
                    conv = convert(int(group[0]), int(group[1]))
                    repl = "[[%s|%s]]" % (group[0], group[1])
                    item[i] = item[i].replace(repl, "£%s" % locale.format("%d", conv, grouping=True))

            item[i] = item[i].replace("[[now]]", "{}".format(get_now("")))
    return item


def convert_picture(item):
    """ 
    Convert occurances of [picture:img|text] to a nicely-formatted pictorial group with caption
    """
    for i in range(len(item)):
        groups = re.findall("\[picture: (?P<pic>.*?)\]", item[i], re.S|re.MULTILINE)
        if not groups is None:
            for pic in groups:
                repl = "[picture: %s]" % pic
                bits = pic.split("|")
                target = """<div class="grid1"><img class="ctrimg" src="https://static.nosher.net/archives/computers/images/extras/{}" alt="{}" title="{}"><p class="desc">{}</p></div>""".format(bits[0], bits[1], bits[1], bits[1])
                item[i] = item[i].replace(repl, target)
    return item


def convert_links(item):
    """
    Convert occurances of [=adid|text], [@company|text], [#model|text] or [!CPU|text] to an HTML link
    """
    for i in range(len(item)):
        for type in ["=", "@", "#", "!"]:
            groups = re.findall("\[{}(?P<ext>.*?)\]".format(type), item[i], re.S|re.MULTILINE)
            if not groups is None:
                for ext in groups:
                    repl = "[{}{}]".format(type, ext)
                    bits = ext.split("|")
                    if len(bits) > 1:
                        url = bits[0]
                        text = bits[1]
                    else:
                        text = url = bits[0]
                    if type == "=":
                        link = url
                    elif type == "#":
                        link = "/archives/computers/model/" + url
                    elif type == "!":
                        link = "/archives/computers/cpus/" + url
                    else:
                        adverts = ArchiveItems.objects.filter(company = url)
                        if len(adverts) == 1:
                            link = adverts[0].adid
                        else:    
                            link = "{}?type=source&value={}".format(ARCHIVES, url)
                    item[i] = item[i].replace(repl, """<a data-link="{}" href="{}">{}</a>""".format(url.replace(" ", "_"), link, text))
    return item


def convert_extras(item):
    """
    Convert occurances of [extra: xxx} to a footnote with a [n] reference.
    Extra tags can contain [extra: image_url|description|width|left/right]. Width
    and left/right are optional
    """
        
    for i in range(len(item)):
        groups = re.findall("\[extra: (?P<ext>.*?)\]", item[i], re.S|re.MULTILINE)
        if not groups is None:
            for ext in groups:
                repl = "[extra: %s]" % ext
                bits = ext.split("|")
                thing = bits[0]
                desc = bits[1]
                if len(bits) > 2:
                    wid = int(bits[2])
                else:
                    wid = 260
                if len(bits) > 3:
                    flot = bits[3]
                else:
                    flot = "right"
                cls = "extra"
                if not flot == "right":
                    cls = "extra_left"
                target = """<img src="https://static.nosher.net/archives/computers/images/extras/%s" style="width: %dpx"/>""" % (thing, wid - 5)
                item[i] = item[i].replace(repl, """<span class="%s" style="width: %spx; float: %s">%s<br />%s</span>""" % (cls, wid, flot, target, desc))
    return item


def convert_images(item):
    """
    Convert occurances of [image: xxx} to a centred image with nicely-formatted description
    """
        
    for i in range(len(item)):
        groups = re.findall("\[image: (?P<img>.*?)\]", item[i], re.S|re.MULTILINE)
        if not groups is None:
            for ext in groups:
                repl = "[image: %s]" % ext
                bits = ext.split("|")
                img = bits[0]
                desc = bits[1]
                target = """<div class="grid1"><img class="ctrimg" src="https://static.nosher.net/archives/computers/images/{}" alt="Image showing {}"><p class="desc">{}</p></div>""".format(img, desc, desc)
                item[i] = item[i].replace(repl, target)
    return item


def create_toc(item):
    toc_count = 0
    updated = []
    toc = []
    for i in range(len(item)):
        line = item[i].strip()
        if line[0:4] == "<h3>":
            title = line.replace("<h3>", "").replace("</h3>", "")
            toc.append("""<a href="#toc{}">{}</a>""".format(toc_count, title))
            updated.append("""<a name="toc{}" ></a>{}""".format(toc_count, line))
            toc_count += 1
        else:
            updated.append(line)
    if len(toc) > 0:
        updated.insert(0, """<div class="toc"><span class="contents">Contents:</span>{}</div>""".format(" • ".join(toc)))
    return updated


def convert_tags(item):
    updated = []
    for i in range(len(item)):
        line = item[i].strip()
        if item[i].strip() == "":
            pass
        elif line[0] is not "<":
            if line == "-origin":
                updated.append("""<p class="origins">This is one of a small set of adverts from before 1975 - the dawn of microcomputers - which help set the scene.</p>""")
            elif line[0] == "~":
                updated.append("""<blockquote class="ref">{}</blockquote>\n""".format(line[1:]))
            elif line[0] == "\\":
                updated.append("""<blockquote class="quote">{}</blockquote>\n""".format(line[1:]))
            else:
                updated.append("<p>{}</p>\n".format(line))
        else: 
            updated.append(item[i])
    return updated 


def convert_acronyms(item):
    for i in range(len(item)):
        for k, v in TLAS.items():
            item[i] = item[i].replace(k, v)
    return item 


def soft_url(value):
    return value.replace("/","/​").replace("_", "_​") # replace "/ and _" with themselves and a zero-width space


def convert_sources(item):
    g = 1
    sources = [] 
    for i in range(len(item)):
        groups = re.findall("\[source: (?P<src>.*?)\]", item[i], re.S|re.MULTILINE)
        if not groups is None:
            for src in groups:
                repl = "[source: %s]" % src
                item[i] = item[i].replace(repl, """<sup class="src">[<a class="src" href="#%d">%d</a>]</sup>""" % (g, g))
                urls = re.findall("(?P<url>http.*)", src, re.S)
                if not urls is None:
                    for url in urls:
                        src = src.replace(url, """<a href="%s">%s</a>""" % (url, soft_url(url)))
                sources.append(src)
                g += 1

    return (item, sources)


def convert(value, year):
    try:
        now = date.today().year
        for i in range(year, now):
                yr = "{}".format(i)
                if yr in INFLATION:
                    value *= (1.0 + INFLATION[yr]/100.0)

        if value < 100:
            return int(value)
        elif value < 10000:
            return (int(value / 10.0) * 10)
        else: 
            return (int(value / 100.0) * 100)
            
    except Exception:
        print("ERR parsing {} {}".format(value, year))
        print(sys.exc_info()[0])
        return -1
