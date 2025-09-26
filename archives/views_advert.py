import os
import re

from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count

from stat import *
from datetime import datetime
from datetime import timedelta
from .models import ArchiveItems
from ..constants import *
from PIL import Image
from pytz import timezone

from .views_template_filters import *

ARCHIVES = "/archives/computers"
ARCHIVEROOT = "/home/httpd/nosher.net/docs" + ARCHIVES
EMAIL = "microhistory@nosher.net"


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


def _get_page_image(img):
    return "{}/{}/images/{}".format(WEBROOT, DOCROOT, img)


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

    body = None
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
    advert_id = adid.split(",")[0]
    items = ArchiveItems.objects.all().order_by('year')
    companies = ArchiveItems.objects.all().values('company').annotate(total = Count('company')).order_by('company')
    try:
        item = ArchiveItems.objects.get(Q(adid__startswith = (advert_id + ",")) | Q(adid = advert_id))
    except ObjectDoesNotExist:
        return _get_null_advert(request, companies)
    
    company_name = item.company
    related = ArchiveItems.objects.filter(company = company_name).order_by('year')
    ad_year = item.year[0:4]
    more_year = ArchiveItems.objects.filter(year__startswith = ad_year)
    moreyear = ad_year if len(more_year) > 1 else None
    title = body = None
    path = os.path.join(ROOT, "{}.txt".format(advert_id))
    imgpath = os.path.join(ROOT, "images", "{}-m.webp".format(advert_id))
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
    body = create_toc(body)
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
        'adid': advert_id,
        'page_image': _get_page_image("{}-m.webp".format(advert_id)),
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
