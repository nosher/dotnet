from django.urls import path

from . import views

urlpatterns = [
    path('computers/', views.computer_index, name='computers'),
    path('computers/timelines', views.timelines, name='timelines'),
    path('computers/index/list', views.list, name='list'),
    path('computers/index', views.catalogue, name='catalogue'),
    path('computers/index/<str:alpha>', views.catalogue, name='catalogue'),
    path('computers/links/computers.svg', views.svg, name='svg'),
    path('computers/links/', views.links, name='links'),
    path('computers/years/', views.computer_filter_years, name='year'),
    path('computers/years/<str:year>', views.computer_filter_year, name='year'),
    path('computers/models/', views.computer_filter_models, name='models'),
    path('computers/models/sorted', views.computer_filter_models_sorted, name='models_sorted'),
    path('computers/model/<str:model>', views.computer_filter_model, name='model'),
    path('computers/<str:advert>', views.computer_advert, name='advert'),
    path('computers/companies/<str:company>', views.computer_filter_company, name='company'),
    path('computers/cpus/', views.computer_filter_cpus, name='cpus'),
    path('computers/cpus/<str:cpu>', views.computer_filter_cpu, name='cpu'),
]
