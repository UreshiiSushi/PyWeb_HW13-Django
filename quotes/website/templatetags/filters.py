from django import template
from ..models import Author

register = template.Library()


def get_author(id_):
    author = Author.objects.get(pk=id_)
    return author.fullname


def get_tags(quote):
    return quote.tags.all()


register.filter("tags", get_tags)
register.filter("author", get_author)
