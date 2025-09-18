
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import redirect

from stat import *
from .models import ArchiveItems
from ..constants import *
from collections import OrderedDict

ARCHIVES = "/archives/computers"
ARCHIVEROOT = "/home/httpd/nosher.net/docs" + ARCHIVES
EMAIL = "microhistory@nosher.net"


def computer_filter_company(request, company):
    return HttpResponse("Hello, world. You're at the computer archives filtered by company.")


def computer_filter_models(request):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.exclude(model__isnull = True).exclude(model__exact = "").values("company","model").annotate(count=Count("cpu")).order_by('company', 'model')
    models = {}
    for r in records:
        company = r["company"]
        first = company[0:1]

        if not first in models:
            models[first] = {}

        if not company in models[first]:
            models[first][company] = []

        existing = models[first][company]
        mods = r["model"].split(",")
        for m in mods:
            m = m.strip()
            if not m in existing:
                existing.append(m)
        models[first][company] = existing

    dict(sorted(models.items()))
    context = { 
        'models': models,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'companies': companies,
        'feedback': EMAIL,
    }
    return render(request, 'computers/models.html', context)


def computer_filter_model(request, model):
    params = request.GET
    model = model.replace("|", "/") # see views_template_filters::encodeslash for why this is here
    company = params.get("company")
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.filter(
                (Q(model__contains = model + ",") | Q(model__contains = "," + model) | Q(model = model))
              ).order_by('year')
    if len(records) == 1:
        return redirect("/archives/computers/{}".format(records[0].adid))
    else:    
        company = records[0].company
        same = True
        for i in range(1, len(records)):
            if records[i].company != company:
                same = False
                continue
        # a hack for now - there are a few "model" names that shouldn't be preceded with "the"
        INDEFINITES = ["CompuServe", "Micronet 800", "Prestel", "MS-DOS", "Multiplan", "MSX", "VisiCalc"]
        if not same or model in INDEFINITES:
            title = model
        elif model[0:len(company)] == company:
            title = "the {}".format(model)
        else:
            title = "the {} {}".format(company, model)

        context = { 
            'model': model,
            'ads': records,
            'title': title,
            'staticServer': WEBROOT,
            'home': ARCHIVES,
            'url': "{}/{}".format(WEBROOT, DOCROOT),
            'companies': companies,
            'feedback': EMAIL,
        }
        return render(request, 'computers/model.html', context)


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
        'ads': allads,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'companies': companies,
        'feedback': EMAIL,
    }
    return render(request, 'computers/years.html', context)


def computer_filter_year(request, year):
    return HttpResponse("Hello, world. You're at the computer archives filtered by year.")


def computer_filter_cpus(request):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.exclude(cpu__isnull = True).exclude(cpu__exact = "").values("cpu").annotate(count=Count("cpu")).order_by('-count', 'cpu')
    display = []
    for r in records:
        text = ""
        sub = ""
        bits = ""
        opts = r["cpu"].split(",")
        if len(opts) > 1:
            c1 = CPUS[opts[0].strip()]
            c2 = CPUS[opts[1].strip()]
            text = "{} and {}".format(c1["name"], c2["name"])
            sub = ""
            bits = c2["bits"] if int(c2["bits"]) > int(c1["bits"]) else c1["bits"]
        else:
            info = CPUS[opts[0]]
            text = "{}".format(info["name"])
            mem = int(pow(2, int(info["add"]))/1024)
            memd = str(mem) + "K" if mem < 1024 else str(int(mem/1024)) + "M"
            sub = "{} bit address ({} memory max)". format(info["add"], memd)
            bits = info["bits"]
            if "note" in info and info["note"]:
                sub = sub + ", {}".format(info["note"])
        display.append({"cpu": r["cpu"], "count": r["count"], "bits": bits, "disp": text, "sub": sub})
    bits = []
    for c in CPUS:
        cpu = CPUS[c]
        if not cpu["bits"] in bits:
            bits.append(cpu["bits"])
    display.sort(key = lambda x: x['disp'])
    context = {
        'cpus': display,
        'bits': bits,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'companies': companies,
        'feedback': EMAIL,
    }
    return render(request, 'computers/cpus.html', context)


def computer_filter_cpu(request, cpu):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.filter(cpu = cpu).order_by('year')
    cpus = cpu.split(",")
    title = ""
    if len(cpus) > 1:
        c1 = CPUS[cpus[0].strip()]["name"]
        c2 = CPUS[cpus[1].strip()]["name"]
        title = "{} and {}".format(c1, c2)
    else:
        info = CPUS[cpus[0].strip()]
        title = "{}".format(info["name"])

    if len(records) == 1:
        return redirect("/archives/computers/{}".format(records[0].adid))
    else:    
        context = {
            'ads': records,
            'title': title,
            'staticServer': WEBROOT,
            'home': ARCHIVES,
            'url': "{}/{}".format(WEBROOT, DOCROOT),
            'companies': companies,
            'feedback': EMAIL,
        }
        return render(request, 'computers/cpu.html', context)


