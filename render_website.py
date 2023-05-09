from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from more_itertools import chunked
from pathlib import Path

    
def on_reload():

    with open("books.json", "r") as json_file:
        json_books_feateres = json_file.read()
    json_books_feateres = json.loads(json_books_feateres)    
    for number, books_feateres in enumerate(json_books_feateres):
        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('template.html')
        rendered_page = template.render(
            books_feateres=list(chunked(books_feateres, 2)),
            current_page=number,
            pages_number=len(json_books_feateres),
        )
        current_dir = Path.cwd() / 'pages'
        Path(current_dir).mkdir(parents=True, exist_ok=True)
        file_name = f'index{number}.html'
        filepath = Path() / current_dir / file_name 
        with open(filepath, 'w', encoding="utf8") as file:
            file.write(rendered_page)