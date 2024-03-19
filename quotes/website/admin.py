from django.contrib import admin
from .models import Author, Quotes, Tag

admin.site.register(Author)
admin.site.register(Quotes)
admin.site.register(Tag)
