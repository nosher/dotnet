from django.urls import path

from . import views

urlpatterns = [
    
    path('api/latest', views.api_latest, name='api'),
    path('api/years', views.api_years, name='api'),
    path('api/year/<str:album_year>', views.api_year, name='api'),
    path('api/<str:album_year>/<str:album_path>', views.api_album, name='api'),
    
    path('', views.index, name='images'),
    path('nojs', views.nojs, name='nojs'),
    path('best/', views.best_of_index, name='best_of_index'),
    path('best/<str:best_of>', views.best_of, name='best_of'),
    path('<str:album_year>', views.year, name='year'),
    path('<str:album_year>/', views.year, name='year'),
    path('<str:album_year>/<str:album_path>', views.album, name='album'),
    path('<str:album_year>/<str:album_path>/', views.album, name='album'),
    path('<str:album_year>/<str:album_path>/<int:index>', views.album, name='album'),
]
