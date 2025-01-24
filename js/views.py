from django.views.decorators.http import require_GET
from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.conf import settings

CACHE = {};

@require_GET
def js(_, filename):

    if filename in CACHE and not settings.DEBUG:
        return HttpResponse(
            CACHE[filename], 
            content_type="text/javascript"
        )
    
    path = "/home/httpd/django/nosher/js/{}".format(filename);
    with open(path) as JS:
        content = JS.readlines()
        CACHE[filename] = content
        return HttpResponse(
            content, 
            content_type="text/javascript"
        )

    raise Http404("File does not exist")