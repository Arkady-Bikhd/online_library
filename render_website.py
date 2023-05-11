import argparse
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from pathlib import Path

    
def on_reload():

    json_file_name = get_user_file()
    print(json_file_name)
    with open(json_file_name, 'r') as json_file:
        json_books_features = json.load(json_file) 
    books_per_page_count = 20
    json_books_features = list(chunked(json_books_features, books_per_page_count))
    for number, books_features in enumerate(json_books_features):
        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('template.html')
        columns_count = 2
        rendered_page = template.render(
            books_features=list(chunked(books_features, columns_count)),
            current_page=number,
            pages_number=len(json_books_features),
        )
        current_dir = Path.cwd() / 'pages'
        Path(current_dir).mkdir(parents=True, exist_ok=True)
        file_name = Path() / current_dir / f'index{number}.html'        
        with open(file_name, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def get_user_file():
     
    parser = argparse.ArgumentParser(
        description='Программа формирует оффлайн-библиотеку',               
    )
    parser.add_argument('-f', '--json_file', default='books.json', help='Имя json-файла')
    
    args = parser.parse_args()
    return args.json_file