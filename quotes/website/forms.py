from django.forms import (
    ModelForm,
    CharField,
    TextInput,
    DateField,
    ModelChoiceField,
    Select,
)
from .models import Tag, Author, Quotes


class TagForm(ModelForm):

    name = CharField(min_length=3, max_length=25, required=True, widget=TextInput())

    class Meta:
        model = Tag
        fields = ["name"]


class AuthorForm(ModelForm):

    fullname = CharField(min_length=3, max_length=50, required=True, widget=TextInput())
    born_date = CharField(
        min_length=6, max_length=25, required=True, widget=TextInput()
    )
    born_location = CharField(
        min_length=3, max_length=50, required=True, widget=TextInput()
    )
    description = CharField(
        min_length=10, max_length=3000, required=True, widget=TextInput()
    )

    class Meta:
        model = Author
        fields = ["fullname", "born_date", "born_location", "description"]


class QuoteForm(ModelForm):

    # author = CharField(min_length=3, max_length=50, required=True, widget=TextInput())
    author = ModelChoiceField(queryset=Author.objects.all(), widget=Select())
    quote = CharField(min_length=3, max_length=250, required=True, widget=TextInput())

    class Meta:
        model = Quotes
        fields = ["author", "quote"]
        exclude = ["tags"]
