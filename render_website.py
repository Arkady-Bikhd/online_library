from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server


def rebuild():
    ... # do things
    print("Site rebuilt")

rebuild()



def load_book_feateres():

    with open("books.json", "r") as json_file:
        book_feateres = json_file.read()
    return json.loads(book_feateres)            
    
def rebuild():
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

server = Server()

server.watch('template.html', rebuild)

server.serve(root='.')
