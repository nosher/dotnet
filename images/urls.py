from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='images'),
    path('<str:album_year>', views.year, name='year'),
    path('<str:album_year>/', views.year, name='year'),
    path('<str:album_year>/<str:album_path>', views.album, name='album'),
    path('<str:album_year>/<str:album_path>/', views.album, name='album'),
    path('<str:album_year>/<str:album_path>/<int:index>', views.album, name='album'),
]
