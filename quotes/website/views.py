from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Author, Quotes, Tag
from .forms import TagForm, AuthorForm, QuoteForm
from bs4 import BeautifulSoup
import json
import requests


def bigbutton_ok(request):
    return redirect(to="website:index")


def bigbutton(request):
    def scrappy_do(url):
        html_doc = requests.get(url)
        return BeautifulSoup(html_doc.text, "lxml")

    def quote_miner(quote):
        found_quote = {}
        tags_list = [tag.text for tag in quote.find_all("a", class_="tag")]
        found_quote["tags"] = tags_list
        found_quote["author"] = quote.find("small", class_="author").text
        found_quote["quote"] = (
            quote.find("span", class_="text").text.replace("“", "").replace("”", "")
        )

        return found_quote

    def scooby_do():
        url = "http://quotes.toscrape.com/page/"
        page = 1
        author_links = {}
        quotes_list = []
        soup = scrappy_do(url + f"{page}/")

        while (quotes := soup.find_all("div", class_="quote")) != []:
            for quote in quotes:
                quotes_list.append(quote_miner(quote))

            authors = soup.find_all("small", class_="author")
            a_links = [quote.find_all("a")[0]["href"] for quote in quotes]

            for i in range(len(a_links)):
                author_links[authors[i].text] = a_links[i]

            page += 1
            soup = scrappy_do(url + f"{page}/")

        return author_links, quotes_list

    def writer_info(links):
        authors_list = []
        url = "http://quotes.toscrape.com"
        for name in links:
            author = {}
            author["fullname"] = name
            result = scrappy_do(url + f"{links[name]}/")
            author["born_date"] = result.find("span", class_="author-born-date").text
            author["born_location"] = result.find(
                "span", class_="author-born-location"
            ).text
            author["description"] = result.find(
                "div", class_="author-description"
            ).text.strip()
            authors_list.append(author)

        return authors_list

    def check_len(string: str, length: int) -> str:
        if len(string) > length:
            return string[:length]
        return string

    def tags_save():
        deleted_tags = Tag.objects.all()
        deleted_tags.delete()
        with open("quotes.json", "r") as file:
            quotes = json.load(file)
        unique_tags = set()
        for item in quotes:
            for tag in item["tags"]:
                unique_tags.add(check_len(tag, 30))
        for item in unique_tags:
            tag = Tag(name=item)
            tag.save()

    def authors_save():
        deleted_authors = Author.objects.all()
        deleted_authors.delete()
        with open("authors.json", "r") as file:
            authors = json.load(file)
        for item in authors:
            author = Author(
                fullname=check_len(item["fullname"], 50),
                born_date=check_len(item["born_date"], 50),
                born_location=check_len(item["born_location"], 50),
                description=check_len(item["description"], 3000),
            )
            author.save()

    def quotes_save():
        deleted_quotes = Quotes.objects.all()
        deleted_quotes.delete()
        with open("quotes.json", "r") as file:
            quotes = json.load(file)
        i = 1
        for item in quotes:
            # tags = [Tag(name=tag) for tag in item["tags"]]
            clear_author = check_len(item["author"], 50)
            author = Author.objects.filter(fullname=clear_author)[:1]
            quote = Quotes(i, author[0].id, check_len(item["quote"], 250))
            i += 1
            quote.save()

            tags = Tag.objects.filter(name__in=item["tags"])
            # tags = [Tag(name=tag) for tag in item["tags"]]
            for tag in tags.iterator():
                quote.tags.add(tag)

    if request.method == "POST":
        author_links, quote_list = scooby_do()
        with open("quotes.json", "w") as fp:
            json.dump(quote_list, fp)
        with open("authors.json", "w") as fp:
            json.dump(writer_info(author_links), fp)
        tags_save()
        authors_save()
        quotes_save()
        return render(request, "website/bb_ok.html")

    return render(request, "website/bb.html")


# ------------------------------- The end of Scraper -----------------------------------


def ten_popular_tags():
    dict_tags = {}
    tags = Tag.objects.all()
    for tag in tags:
        quantity = Tag.objects.get(id=tag.id).quotes_set.all().count()
        dict_tags[tag.name] = quantity
    sorted_tuple_tags = sorted(dict_tags.items(), key=lambda x: x[1], reverse=True)[:10]
    top_tags = []
    for tag in sorted_tuple_tags:
        top_tags.append(tag[0])
    return top_tags


def index(request, page=1):
    quotes_list = Quotes.objects.all()
    ten_tags = ten_popular_tags()
    shift = 10

    paginator = Paginator(list(quotes_list), shift)
    if page > paginator.num_pages:
        return render(request, "website/404.html")
    quotes_on_page = paginator.page(page)

    return render(
        request,
        "website/index.html",
        {"quotes": quotes_on_page, "ten_popular_tags": ten_tags},
    )


def author(request, author_id):
    author = Author.objects.get(pk=author_id)
    return render(request, "website/author.html", context={"author": author})


def tag(request, tag_name):
    # It's need to push also Quotes with tag_id !
    # tag = Tag.objects.get(name=tag_name)
    quotes = Tag.objects.get(name=tag_name).quotes_set.all()
    return render(
        request, "website/tag.html", context={"tag": tag_name, "quotes": quotes}
    )


@login_required
def tags(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="website:index")
        else:
            return render(request, "website/tags.html", {"form": form})

    return render(request, "website/tags.html", {"form": TagForm()})


@login_required
def authors(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="website:index")
        else:
            return render(request, "website/authors.html", {"form": form})

    return render(request, "website/authors.html", {"form": AuthorForm()})


@login_required
def quotes(request):
    tags = Tag.objects.all()
    authors = Author.objects.all()
    quote_id = Quotes.objects.all().count()

    if request.method == "POST":
        form = Quotes(quote_id + 1, request.POST["author"], request.POST["quote"])
        # if form.is_valid():
        form.save()

        choice_tags = Tag.objects.filter(name__in=request.POST.getlist("tags"))
        for tag in choice_tags.iterator():
            form.tags.add(tag)

        return redirect(to="website:index")
    # else:
    # return render(
    #     request,
    #     "website/quotes.html",
    #     {"tags": tags, "form": QuoteForm()},
    # )

    return render(
        request,
        "website/quotes.html",
        {"tags": tags, "form": QuoteForm()},
    )
