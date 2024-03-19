from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:page>", views.index, name="root_paginate"),
    path("bigbutton", views.bigbutton, name="bigbutton"),
    path("bigbutton_ok", views.bigbutton_ok, name="bigbutton_ok"),
    path("tags/", views.tags, name="tags"),
    path("authors/", views.authors, name="authors"),
    path("quotes/", views.quotes, name="quotes"),
    path("author/<int:author_id>", views.author, name="author"),
    path("tag/<str:tag_name>", views.tag, name="tag"),
]
