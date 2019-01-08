from django.urls import path

from . import views

urlpatterns = [
    path('<str:section>/', views.content, name='content'),
    path('<str:section>/<str:page>', views.content_page, name='content_page'),
]
