from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from more_itertools import chunked

def load_book_feateres():

    with open("books.json", "r") as json_file:
        json_book_feateres = json_file.read()
    json_book_feateres = json.loads(json_book_feateres)
    book_feateres = list()
    for books in json_book_feateres:
        for book in books:
            book_feateres.append(book)       
    return list(chunked(book_feateres, 2))            
    
def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    rendered_page = template.render(
        book_feateres = load_book_feateres(),
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)