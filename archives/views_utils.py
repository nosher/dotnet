import os

from django.shortcuts import render

from stat import *
from datetime import datetime
from datetime import timedelta
from ..constants import *
from PIL import Image
from pytz import timezone

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


def _get_null_advert(request, companies):
    """
    Used for testing and as a 404. Invoke the advert /archives/computers/foo(?yesterday|sameday|twoday|None)
    """
    params = request.GET
    created = datetime.strptime('Jan 1 2025', '%b %d %Y').date()
    item = {"source": "The Bureau of Lost and Found", "company": "404", "year": "2025-02-00", "date_created": created}
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
        'page_title': "404 Missing Page",
        'staticServer': WEBROOT,
        'page_description': "A description for missing content",
        'next': None,
        'prev': None,
        'nextany': None,
        'prevany': None,
        'home': ARCHIVES,
        'title': "Missing Content",
        'logo': _get_logo("Commodore"),
        'body': "<p>There's nothing here, sorry. Try clicking on the links below...</p>",
        'sources': ["foo"],
        'mtime': updated,
        'companies': companies,
        'related': [],
        'feedback': EMAIL,
    }
    return render(request, 'computers/advert.html', context)
