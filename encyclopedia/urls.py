from django.urls import path

from . import views

app_name = "wiki"

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>", views.search, name="search"),
    path("similar/", views.similar, name="similar"),
    path("create/", views.create, name="create"),
    path("modify/<str:name>", views.modify, name="modify"),
    path("random/", views.random, name="random"),
]
