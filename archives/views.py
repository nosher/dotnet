import base64

from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from django.views.decorators.clickjacking import xframe_options_sameorigin

from stat import *
from datetime import datetime
from .models import ArchiveItems
from ..constants import *

from .views_filters import *
from .views_advert import *
from .views_template_filters import *

ARCHIVES = "/archives/computers"
ARCHIVEROOT = "/home/httpd/nosher.net/docs" + ARCHIVES
EMAIL = "microhistory@nosher.net"


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


