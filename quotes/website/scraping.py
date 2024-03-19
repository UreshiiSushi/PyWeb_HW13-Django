from bs4 import BeautifulSoup
import json
import requests


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


def authors_save():
    authors_dict = {}
    with open("authors.json", "r") as file:
        authors = json.load(file)
    for item in authors:
        Author(
            fullname=item["fullname"],
            born_date=item["born_date"],
            born_location=item["born_location"],
            description=item["description"],
        ).save()


def quotes_save():
    with open("quotes.json", "r") as file:
        quotes = json.load(file)
    for item in quotes:
        tags = [Tag(name=tag) for tag in item["tags"]]
        Quotes(
            tags=tags,
            author=authors_dict[item["author"]],
            quote=item["quote"],
        ).save()


if __name__ == "__main__":
    author_links, quote_list = scooby_do()
    with open("quotes.json", "w") as fp:
        json.dump(quote_list, fp)
    with open("authors.json", "w") as fp:
        json.dump(writer_info(author_links), fp)
    authors_save()
    quotes_save()
