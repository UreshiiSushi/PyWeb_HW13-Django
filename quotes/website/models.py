from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.name}"


class Author(models.Model):
    fullname = models.CharField(max_length=50, unique=True)
    born_date = models.CharField(max_length=50)
    born_location = models.CharField(max_length=50)
    description = models.CharField(max_length=3000)

    def __str__(self):
        return f"{self.fullname}"


class Quotes(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    quote = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.author} {self.quote} {self.tags}"
