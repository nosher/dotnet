import os
import re
import locale
import sys
import base64

from django.db.models import Count
from django.db.models.functions import Substr
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.template.defaulttags import register
from django.contrib.humanize.templatetags.humanize import ordinal
from django.db.models import Count
from django.views.decorators.clickjacking import xframe_options_sameorigin

from stat import *
from datetime import datetime
from datetime import date
from datetime import timedelta
from .models import ArchiveItems
from ..constants import *
from collections import OrderedDict
from PIL import Image
from pytz import timezone

ARCHIVES = "/archives/computers"
ARCHIVEROOT = "/home/httpd/nosher.net/docs" + ARCHIVES
EMAIL = "microhistory@nosher.net"


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
    Convert occurances of [=adid|text], [@company] or [@company|text] to an HTML link
    """
    for i in range(len(item)):
        for type in ["=", "@"]:
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
                    else:
                        adverts = ArchiveItems.objects.filter(company = url)
                        if len(adverts) == 1:
                            link = adverts[0].adid
                        else:    
                            link = "{}?type=source&value={}".format(ARCHIVES, url)
                    item[i] = item[i].replace(repl, """<a data-link="{}" href="{}">{}</a>""".format(url, link, text))
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
def get_first_advert(company):
    # get the first advert for a company - used primary as a shortcut to find the adid for companies
    # which have only a single advert, so we show that instead of a company list
    item = ArchiveItems.objects.filter(company=company)[0]
    return item.adid


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


def catalogue(request, alpha = ""):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    catalogue = OrderedDict()
    if alpha is None or alpha == "":
        alpha = "A"
    with open(ARCHIVEROOT + "/catalogue.dat", encoding="utf-8") as fh:
        blob = fh.readlines()
        for data in blob:
            data = data.replace("\n", "")
            (iword, refs) = data.split("\t")
            first = iword[0:1].upper()
            reflist = OrderedDict() 
            if first in catalogue:
                reflist = catalogue[first]
            reflist[iword] = refs.split(",")
            catalogue[first] = reflist
    context = {
        'title': "Index of adverts",
        'current': alpha,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'alphas': catalogue.keys(),
        'companies': companies,
        'catalogue': catalogue[alpha],
        'feedback': EMAIL,
    }
    return render(request, 'computers/catalogue.html', context)


def links(request):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    encoded = None
    index = None
    with open(ARCHIVEROOT + "/graphs/computers.svg", "rb") as fh:
        svg = fh.read()
        encoded = base64.b64encode(svg)
    with open(ARCHIVEROOT + "/graphs/index.html") as ind:
        index = ind.read()

    context = {
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'companies': companies,
        'feedback': EMAIL,
        'index': index,
        'svgData': encoded.decode("ascii")
    }
    return render(request, 'computers/links.html', context)


@xframe_options_sameorigin
def svg(_):
    svg = None
    with open(ARCHIVEROOT + "/graphs/computers.svg", "rb") as fh:
        svg = fh.read()
    return HttpResponse(svg, content_type="image/svg+xml")


def timelines(request):
    params = request.GET
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    lines = [] 
    filter_param = ""
    sort_param = ""
    sortkey = filterkey = title = ""

    with open(ARCHIVEROOT + "/timeline.dat") as fh:
        for l in [f.strip() for f in fh.readlines()]:
            if l[:1] != "#" and l.strip() != "":
                parts = l.split("|")
                dfrom = _get_date_as_value(parts[1].split("-"), 0)
                dto = _get_date_as_value(parts[2].split("-"), 0.99) 
                geo = ""
                joins = ""
                name = parts[0]

                if len(parts) > 3:
                    geo = parts[3]

                if len(parts) > 4 and parts[4] != "":
                    bits = parts[4].split(":")
                    joins = "{}:{}:{}".format(name, _get_date_as_value(bits[0].split("-"), 0), bits[1])

                data = {"name": name, "from": dfrom, "to": dto, "range": (dto - dfrom), "geo": geo, "joins": joins}
                lines.append(data)

    if "filter" in params:
        filterkey = params.get("filter")
        if filterkey in ["UK", "US"]:
            lines = list(filter(lambda x: x["geo"] == filterkey, lines))
            filter_param = "&filter={}".format(filterkey)

    if "sort" in params:
        sortkey = params.get("sort")
        sort_param = "&sort={}".format(sortkey)
        if sortkey in data:
            lines = sorted(lines, key = lambda d: d[sortkey])

    context = {
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'companies': companies,
        'timelines': lines,
        'rows': len(lines),
        'now': datetime.now().year,
        'filter': filter_param,
        'sort': sort_param,
        'sortkey': sortkey,
        'filterkey': filterkey,
        'feedback': EMAIL,
    }

    return render(request, 'computers/timeline.html', context)


def _get_date_as_value(dte, offset):
    if dte[0] == "*":
        return datetime.now().year + offset 
    return int(dte[0]) + (float(dte[1])/12.0 if len(dte) > 1 else offset) \


def computer_index(request):
    titles = {}
    summaries = {}
    params = request.GET
    items = []
    item = {}
    title = ""
    offset = 0
    page = pagination = 15
    urlparams = []
    intro = ""
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    company_name = None

    # check for an offset
    if "offset" in params:
        offset = int(params.get("offset"))
   
    if "type" in params and "value" in params: 
            ptype = params.get("type")
            value = params.get("value")
            urlparams.append("type={}".format(ptype))
            urlparams.append("value={}".format(value))
            # check for a company 
            if ptype == "source":
                company_name = value
                items = ArchiveItems.objects.filter(company = company_name).order_by('year')
                title = "{} adverts".format(value)
                item["company"] = value
            # check for a year
            elif ptype == "year":
                items = ArchiveItems.objects.filter(year__startswith=value).order_by('year')
                title = "{} adverts".format(value)
            section = page_title = title
    else:
        # otherwise, default to most-recently-created adverts
        items = ArchiveItems.objects.order_by('-date_created')
        title = page_title = "A history of the microcomputer industry in 300 adverts"
        section = "adverts"
        if offset == 0:
            with open(ARCHIVEROOT + "/intro.txt", encoding="utf-8") as fh:
                intro = fh.read()
        else:
            intro = ""

    # if total items count is close to page, then set page to the total, so 
    # we don't get "next 1 items"
    if len(items) - (offset + page) < 4:
        page = len(items) - offset

    selected = []
    for n in range(offset, offset + page):
        i = items[n]
        selected.append(i)
        adid = i.adid
        # remove any multi-advert reference
        adid = adid.split(",")[0]
        i.adid = adid
        with open(os.path.join(ROOT, "{}.txt".format(adid)), encoding="utf-8") as fh:
            lines = fh.readlines()
            titles[adid] = lines[0]
            summaries[adid] = convert_to_text(lines[1:])
 
    # determine next and previous 
    nextparams = []
    prevparams = []
    if offset + page < len(items):
        nextparams.extend(urlparams)
        nextparams.append("offset={}".format(offset + page))
    if offset > 0:
        prevparams.extend(urlparams)
        prevparams.append("offset={}".format(offset - pagination))
 
    context = {
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'title': title,
        'section': section,
        'item': item,
        'page_image': _get_page_image("{}-m.webp".format(items[0].adid)),
        'page_title': page_title,
        'page_description': re.sub("<.*?>","", intro),
        'staticServer': WEBROOT,
        'titles': titles,
        'home': ARCHIVES,
        'intro': intro,
        'isFiltered': (company_name is not None and company_name != ""),
        'logo': _get_logo(company_name),
        'summaries': summaries,
        'items': selected,
        'page': page,
        'next': "?" + "&".join(nextparams) if len(nextparams) > 0 else None,
        'next_count': (page if offset + (page * 2) < len(items) else len(items) - offset - page),
        'prev': "?" + "&".join(prevparams) if len(prevparams) > 0 else None,
        'prev_count': (pagination if offset > 0 else 0),
        'companies': companies,
        'feedback': EMAIL,
    }
    return render(request, 'computers/list.html', context)


def computer_advert(request, advert):
    adid = advert.split(",")[0]
    if (adid[-4:] == ".txt"):
        return computer_advert_text(request, adid)
    else:
        return computer_advert_html(request, adid)


def computer_advert_text(request, adid):

    title = body = None
    path = os.path.join(ROOT, adid)
    idx = request.GET.get("idx", "")

    # get advert contents
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
        if len(lines) > 1:
            title = lines[0]
            body = lines[1:]
        else: 
            title = "A history of the computer industry in 300 adverts"
            body = lines

    body = convert_values(body)
    body = convert_acronyms(body)
    body = "".join(body)
    # remove HTML, etc
    body = re.sub("<.*?>", "", body)
    body = re.sub("\[extra.*?\]", "", body)
    body = re.sub("\[image.*?\]", "", body)
    body = re.sub("\[source.*?\]", "", body)
    page = 330
 
    if not idx == "":
        pos = body.find(idx)
        orig_len = len(body)
        start = 0 if pos < 100 else pos - 100
        end = start + page 
        if end > orig_len and orig_len > page:
            end = orig_len
            start = end - page
        body = body[start:end]
        if (start > 0): body = "..." + body
        if (end < orig_len): body = body + "..."
        body = re.sub(idx, "<span class=\"hilite\">{}</span>".format(idx), body)
    else:
        body = body[0:330] 
    context = {
        'body': body,
        'staticServer': WEBROOT,
    }
    response = render(request, 'computers/text_advert.html', context, content_type="text/plain; charset=UTF-8")
    return HttpResponse(response, content_type="text/plain; charset=UTF-8")


def computer_advert_html(request, adid):
    adid = adid.split(",")[0]
    items = ArchiveItems.objects.all().order_by('year')
    companies = ArchiveItems.objects.all().values('company').annotate(total = Count('company')).order_by('company')
    adverts = ArchiveItems.objects.filter(adid__startswith = adid)
    item = None
    if len(adverts) > 0:
        item = adverts[0]
    else:
        return _get_null_advert(request, companies)
    company_name = item.company
    related = ArchiveItems.objects.filter(company = company_name).order_by('year')
    ad_year = item.year[0:4]
    more_year = ArchiveItems.objects.filter(year__startswith = ad_year)
    moreyear = ad_year if len(more_year) > 1 else None
    title = body = None
    path = os.path.join(ROOT, "{}.txt".format(adid))
    imgpath = os.path.join(ROOT, "images", "{}-m.webp".format(adid))
    idx = request.GET.get("idx", "")
    stats = os.stat(path)
    fmt_date = datetime.fromtimestamp(stats[ST_MTIME]).replace(tzinfo = timezone('UTC'))
    mysql_date = item.date_created.replace(tzinfo = timezone('UTC'))
    updated = _get_updated(fmt_date, mysql_date)

    # get image size
    im = Image.open(imgpath)
    (imgw, imgh) = im.size

    # compensate for hi-res images
    if imgw > 1200 or imgh > 1200:
        imgw = int(imgw / 2)
        imgh = int(imgh / 2)

    # get advert contents
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
        if len(lines) > 1:
            title = lines[0].strip()
            body = lines[1:]
        else: 
            title = "A history of the computer industry in 300 adverts"
            body = lines

    raw_body = convert_to_text(body)

    body = convert_tags(body)
    body = convert_values(body)
    body = convert_acronyms(body)
    body = convert_extras(body)
    body = convert_picture(body)
    body = convert_links(body)
    body = convert_images(body)
    (body, sources) = convert_sources(body)
    body = "".join(body)
    body = body.replace("{{staticServer}}", WEBROOT)

    # determine navigation
    nxt = prv = None
    for i in range(len(related)):
        if related[i].adid == item.adid:
            if i > 0:
                prv = related[i - 1]
                prv.adid = prv.adid.split(",")[0]
            if i < len(related) - 1:
                nxt = related[i + 1] 
                nxt.adid = nxt.adid.split(",")[0]
    
    nxtany = prvany = None
    for i in range(len(items)):
        if items[i].adid == item.adid:
            if i > 0:
                prvany = items[i - 1]
                prvany.adid = prvany.adid.split(",")[0]
            if i < len(items):
                nxtany = items[i + 1] 
                nxtany.adid = nxtany.adid.split(",")[0]

    page_title = "{} advert: {}".format(item.company, re.sub("<.*?>", "", title))
    
    if not idx == "":
        title = title.replace(idx, "<span class='hilite'>{}</span>".format(idx))
        body = body.replace(idx, "<span class='hilite'>{}</span>".format(idx))
        body = body.replace(idx.lower(), "<span class='hilite'>{}</span>".format(idx.lower()))
        body = body.replace(idx.replace(" ","-"), "<span class='hilite'>{}</span>".format(idx.replace(" ", "-")))

    context = {
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'adid': adid,
        'page_image': _get_page_image("{}-m.webp".format(adid)),
        'width': imgw,
        'height': imgh,
        'aspect': (imgw / imgh),
        'item': item,
        'page_title': page_title,
        'staticServer': WEBROOT,
        'page_description': raw_body,
        'moreyear': moreyear,
        'next': nxt,
        'prev': prv,
        'nextany': nxtany,
        'prevany': prvany,
        'home': ARCHIVES,
        'title': "{} Advert - {}".format(item.company, get_year(item.year)),
        'advert_title': title,
        'logo': _get_logo(company_name),
        'body': body,
        'sources': sources,
        'mtime': updated,
        'companies': companies,
        'related': related,
        'feedback': EMAIL,
    }
    return render(request, 'computers/advert.html', context)


def computer_filter_company(request, company):
    return HttpResponse("Hello, world. You're at the computer archives filtered by company.")


def computer_filter_model(request, model):
    return HttpResponse("Hello, world. You're at the computer archives filtered by model.")


def computer_filter_years(request):
    records = ArchiveItems.objects.all().order_by('year')
    allads = OrderedDict() 
    for ad in records:
        year = int(ad.year[0:4])
        if not year in allads.keys():
            allads[year] = [ad]
        else:
            a = allads[year]
            a.append(ad)
            allads[year] = a
   
    for k, v in allads.items():
        allads[k] = sorted(v, key = lambda advert: advert.company) 
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    context = {
        'companies': companies,
        'ads': allads,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'feedback': EMAIL,
    }
    return render(request, 'computers/years.html', context)


def computer_filter_year(request, year):
    return HttpResponse("Hello, world. You're at the computer archives filtered by year.")


def _get_page_image(img):
    return "{}/{}/images/{}".format(WEBROOT, DOCROOT, img)


def _get_logo(name):
    if name is not None and name != "":
        name = name.replace(" ", "").replace("-", "").replace("/", "")
        path = ARCHIVEROOT + "/images/logos/{}.webp".format(name)
        if os.path.isfile(path):
            img = Image.open(path) 
            width,height = img.size 
            return {"img": WEBROOT + ARCHIVES + "/images/logos/{}.webp".format(name), "landscape": width / height > 1.4}
    return None


def _get_updated(fmt_date, mysql_date):
    # HACK: all source files got their dates reset to 18 June 2024 at some point, so 
    # ignore this if that's what the date is
    if fmt_date.strftime("%d %B %Y") != "18 June 2024" and fmt_date > (mysql_date + timedelta(days = 1)):  
        return fmt_date.strftime("%d %B %Y") 
    return None


def _get_null_advert(request, companies):
    """
    Used for testing and as a 404. Invoke the advert /archives/computers/foo(?yesterday|sameday|twoday|None)
    """
    params = request.GET
    created = datetime.strptime('Jan 1 2025', '%b %d %Y').date()
    item = {"source": "Out of Nowhere", "company": "404", "year": "2025-02-00", "date_created": created}
    updated = _get_updated(created, created)
    if "twoday" in params:
        updated = _get_updated(created + timedelta(days = 2), created)
    if "sameday" in params:
        updated = _get_updated(created + timedelta(hours = 2), created)
    if "yesterday" in params:
        updated = _get_updated(created + timedelta(days = -2), created)

    context = {
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'adid': "foo",
        'page_image': _get_page_image("i404-m.webp"),
        'width': 700,
        'height': 920,
        'aspect': 0.755,
        'item': item,
        'page_title': "404 Lost Advert",
        'staticServer': WEBROOT,
        'page_description': "A description for a lost advert",
        'next': None,
        'prev': None,
        'nextany': None,
        'prevany': None,
        'home': ARCHIVES,
        'title': "Lost Advert",
        'logo': _get_logo("Commodore"),
        'body': "<p>There's no advert here, sorry.</p>",
        'sources': ["foo"],
        'mtime': updated,
        'companies': companies,
        'related': [],
        'feedback': EMAIL,
    }
    return render(request, 'computers/advert.html', context)