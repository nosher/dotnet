from django.urls import path

from . import views

urlpatterns = [
    path('computers/', views.computer_index, name='computers'),
    path('computers/index', views.catalogue, name='catalogue'),
    path('computers/index/<str:alpha>', views.catalogue, name='catalogue'),
    path('computers/links/', views.links, name='links'),
    path('computers/years/', views.computer_filter_years, name='year'),
    path('computers/years/<str:year>', views.computer_filter_year, name='year'),
    path('computers/<str:advert>', views.computer_advert, name='advert'),
    path('computers/companies/<str:company>', views.computer_filter_company, name='company'),
    path('computers/models/<str:model>', views.computer_filter_model, name='model'),
]
