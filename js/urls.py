from django.urls import path

from . import views

urlpatterns = [
    path('<str:filename>', views.js, name='js'),
]
