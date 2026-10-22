
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
from collections import defaultdict
from .views_utils import _get_null_advert
from .views_utils import _get_az

ARCHIVES = "/archives/computers"
ARCHIVEROOT = "/home/httpd/nosher.net/docs" + ARCHIVES
EMAIL = "microhistory@nosher.net"
CPUS = {                                                        
    "6502": {"name":"MOS Technology 6502", "bits": "8", "add": "16"},
    "6509": {"name":"MOS Technology 6509", "bits": "8", "add": "20", "note": "extra memory accessed via bank switching"},
    "8080": {"name":"Intel 8080", "bits": "8", "add": "16", "note": ""},
    "8085": {"name":"Intel 8085", "bits": "8", "add": "16", "note": "A faster 5V version of 8080"},
    "80C85": {"name":"Intel 80C85", "bits": "8", "add": "16", "note": "CMOS version of 8085"},
    "8086": {"name":"Intel 8086", "bits": "16", "add": "20"},   
    "80C86": {"name":"Intel 80C86", "bits": "16", "add": "20", "note": "CMOS version of 8086"},   
    "8086-2": {"name":"Intel 8086-2", "bits": "16", "add": "20", "note": "faster version of the 8086"},   
    "8088": {"name":"Intel 8088", "bits": "16", "add": "20", "note": "modified version of 8086 with only 8-bit data bus"},    
    "80C88": {"name":"Intel 80C88", "bits": "16", "add": "20", "note": "CMOS version of 8088"},    
    "80186": {"name":"Intel 80186", "bits": "16", "add": "20"}, 
    "80286": {"name":"Intel 80286", "bits": "16", "add": "24"},   
    "80386": {"name":"Intel 80386", "bits": "32", "add": "32"}, 
    "80486": {"name":"Intel 80486", "bits": "32", "add": "32"}, 
    "68000": {"name":"Motorola 68000", "bits": "32", "add": "24", "note": "16-bit data bus"},
    "68008": {"name":"Motorola 68008", "bits": "32", "add": "20", "note": "8 bit data bus"},
    "68020": {"name":"Motorola 68020", "bits": "32", "add": "32"},
    "68030": {"name":"Motorola 68030", "bits": "32", "add": "32"},
    "68040": {"name":"Motorola 68040", "bits": "32", "add": "32"},
    "6800": {"name":"Motorola 6800", "bits": "8", "add": "16"}, 
    "6809": {"name":"Motorola 6809", "bits": "8", "add": "16"}, 
    "6510": {"name":"MOS Technology 6510", "bits": "8", "add": "16", "note": "improved 6502"},
    "6512": {"name":"MOS Technology 6512", "bits": "8", "add": "16", "note": "same as the 6502 but requires an external clock"},
    "SCMP": {"name":"National Semiconductor SC/MP \"Scamp\"", "bits": "8", "add": "16"},
    "Z80": {"name":"Zilog Z80", "bits": "8", "add": "16", "note": "compatible with Intel 8080"},
    "6507": {"name":"MOS Technology 6507", "bits": "8", "add": "13", "note": "modified 6502 with 7-bit data bus"},
    "TMS9900": {"name":"Texas Instruments TMS9900", "bits": "16", "add": "16", "note": "world's first single-chip 16 bit CPU"},
    "WD16": {"name":"Western Digital WD16", "bits": "16", "add": "16"},
    "Z8000": {"name":"Zilog Z8000", "bits": "16", "add": "16", "note": "evolution of Z80"},
    "ARM2": {"name":"Acorn RISC Machines ARM2", "bits": "32", "add": 26},
    "8502": {"name":"MOS Technology 8502", "bits": "8", "add": "16", "note": "improved version of 6510"},
    "V20": {"name":"NEC V20", "bits": "16", "add": "20", "note": "8 bit data bus, compatible with 8088"},
    "V30": {"name":"NEC V30", "bits": "16", "add": "20", "note": "same as V20 but with 16-bit data bus"},
    "7501": {"name":"MOS Technology 7501", "bits": "8", "add": "16", "note": "variant of the 6510"},
    "8501": {"name":"MOS Technology 8501", "bits": "8", "add": "16", "note": "variant of the 6510"},
    "65SC12": {"name":"Western Design Center 65SC12", "bits": "8", "add": "16", "note": "improved CMOS version of the 6502"},
    "PD780C-1": {"name":"NEC PD780C-1", "bits": "8", "add": "16", "note": "compatible with the Zilog Z80A"},
    "mN601G": {"name":"Data General mN601G", "bits": "16", "add": "16"},
    "CDP1802": {"name":"RCA CDP-1802 \"COSMAC\"", "bits": "8", "add": "16", "note": "address bus was 8-bit multiplexed"},
    "6301": {"name":"Hitachi 6301/6309", "bits": "8", "add": "16", "note": "version of Motorola's 6809"},
    "LSI-11": {"name":"Western Digital LSI-11", "bits": "16", "add": "16", "note": "four-chip LSI version of the DEC PDP-11"},
    "6100": {"name":"Intersil 6100", "bits": "12", "add": "12", "note": "CMOS clone of DEC's PDP-8"},
    "Capricorn": {"name":"Hewlett-Packard Capricorn", "bits": "8", "add": "16", "note": "proprietary HP CPU, with built-in advanced maths features. Address bus was 8 bit multiplexed"},
    "FOCUS": {"name":"Hewlett-Packard FOCUS", "bits": "32", "add": "32", "note": "proprietary HP CPU, the first commercial 32-bit chip on the market"},
    "LH5801": {"name":"Sharp LH5801", "bits": "8", "add": "16", "note": "a CMOS chip similar to the Z80"},
} 

def computer_filter_company(request, company):
    return HttpResponse("Hello, world. You're at the computer archives filtered by company.")


def computer_filter_models(request):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.exclude(model__isnull = True).exclude(model__exact = "").values("company","model").annotate(count=Count("cpu")).order_by('company', 'model')
    total = ArchiveItems.objects.exclude(model__isnull = True).exclude(model__exact = "").values("model").distinct().count()
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
        'total': total,
        'models': models,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'companies': companies,
        'az': _get_az(companies),
        'az_key': "A",
        'feedback': EMAIL,
    }
    return render(request, 'computers/models.html', context)


def computer_filter_models_sorted(request):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.exclude(model__isnull = True).exclude(model__exact = "").values("model").order_by('model')
    total = ArchiveItems.objects.exclude(model__isnull = True).exclude(model__exact = "").values("model").distinct().count()
    models = defaultdict(list)
    for r in records:
        mlist = r["model"].split(",")
        for model in mlist:
            first = model[0:1].upper()
            if first in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                first = "0-9"
            existing = models[first]
            if not model in existing:
                existing.append(model)
            existing.sort()
            models[first] = existing
    sortmodels = dict(sorted(models.items(), key=lambda item: item[0]))

    context = { 
        'total': total,
        'models': sortmodels,
        'staticServer': WEBROOT,
        'home': ARCHIVES,
        'url': "{}/{}".format(WEBROOT, DOCROOT),
        'companies': companies,
        'az': _get_az(companies),
        'az_key': "A",
        'feedback': EMAIL,
    }
    return render(request, 'computers/models_sorted.html', context)


def computer_filter_model(request, model):
    params = request.GET
    intro = get_file(model)
    model = model.replace("|", "/") # see views_template_filters::encodeslash for why this is here
    company = params.get("company")
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.filter(
                (Q(model__contains = model + ",") | Q(model__contains = "," + model) | Q(model = model))
              ).order_by('year')
    
    if model == "test" or model == "testintro":
        context = { 
            'model': "test",
            'ads': [],
            'title': "test",
            'intro': "" if model == "test" else "introduction",
            'staticServer': WEBROOT,
            'home': ARCHIVES,
            'url': "{}/{}".format(WEBROOT, DOCROOT),
            'companies': companies,
            'az': _get_az(companies),
            'az_key': "A",
            'feedback': EMAIL,
        }
        return render(request, 'computers/model.html', context)
    elif len(records) == 0:
        return _get_null_advert(request, companies)
    elif len(records) == 1:
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
            'intro': intro,
            'staticServer': WEBROOT,
            'home': ARCHIVES,
            'url': "{}/{}".format(WEBROOT, DOCROOT),
            'companies': companies,
            'az': _get_az(companies),
            'az_key': "A",
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
        'az': _get_az(companies),
        'az_key': "A",
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
        if len(opts) == 2:
            c1 = CPUS[opts[0].strip()]
            c2 = CPUS[opts[1].strip()]
            text = "{} and {}".format(c1["name"], c2["name"])
            sub = ""
            bits = c2["bits"] if int(c2["bits"]) > int(c1["bits"]) else c1["bits"]
        elif len(opts) == 3:
            c1 = CPUS[opts[0].strip()]
            c2 = CPUS[opts[1].strip()]
            c3 = CPUS[opts[2].strip()]
            text = "{}, {} and {}".format(c1["name"], c2["name"], c3["name"])
            sub = ""
            bits = c2["bits"] if int(c2["bits"]) > int(c1["bits"]) else c1["bits"]
        else:
            if opts[0] in CPUS:
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
        'az': _get_az(companies),
        'az_key': "A",
        'feedback': EMAIL,
    }
    return render(request, 'computers/cpus.html', context)


def computer_filter_cpu(request, cpu):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    records = ArchiveItems.objects.filter(cpu = cpu).order_by('year')
    cpus = cpu.split(",")
    title = ""
    intro = get_file(cpu)
    if not cpus[0] in CPUS.keys():
        return _get_null_advert(request, companies)
    
    if len(cpus) > 1:
        c1 = CPUS[cpus[0].strip()]["name"]
        c2 = CPUS[cpus[1].strip()]["name"]
        title = "{} and {}".format(c1, c2)
    else:
        info = CPUS[cpus[0].strip()]
        title = "{}".format(info["name"])

    intro = get_file(cpu)
    if len(records) == 1:
        return redirect("/archives/computers/{}".format(records[0].adid))
    else:    
        context = {
            'ads': records,
            'title': title,
            'intro': intro,
            'staticServer': WEBROOT,
            'home': ARCHIVES,
            'url': "{}/{}".format(WEBROOT, DOCROOT),
            'companies': companies,
            'az': _get_az(companies),
            'az_key': "A",
            'feedback': EMAIL,
        }
        return render(request, 'computers/cpu.html', context)


def catalogue(request, alpha = ""):
    companies = ArchiveItems.objects.all().values('company').annotate(total=Count('company')).order_by('company')
    catalogue = OrderedDict()
    if alpha is None or alpha == "":
        alpha = "A"
    with open(ARCHIVEROOT + "/catalogue_{}.dat".format(alpha), encoding="utf-8") as fh:
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
        'alphas': list("1468ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        'companies': companies,
        'az': _get_az(companies),
        'az_key': "A",
        'catalogue': catalogue[alpha],
        'feedback': EMAIL,
    }
    return render(request, 'computers/catalogue.html', context)


def get_file(name):
    try:
        with open("{}/intros/{}.txt".format(ARCHIVEROOT, name)) as fh:
            intro = fh.readlines()
            return '\n'.join(f"<p>{line.strip()}</p>" for line in intro)
    except FileNotFoundError:
        return None
