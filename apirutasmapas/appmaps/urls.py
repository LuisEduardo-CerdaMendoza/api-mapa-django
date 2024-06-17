from django.urls import path
from appmaps import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/genetico/', views.genetico, name='genetico'),
]
