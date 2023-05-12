import argparse
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

    
def on_reload():

    json_file_path = get_user_file_path()    
    with open(json_file_path, 'r') as json_file:
        books_features = json.load(json_file) 
    books_per_page_count = 20
    page_books_features = list(chunked(books_features, books_per_page_count))
    for number, books_features in enumerate(page_books_features):
        env = Environment(
            loader=FileSystemLoader('.'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('template.html')
        columns_count = 2
        rendered_page = template.render(
            books_features=list(chunked(books_features, columns_count)),
            current_page=number,
            pages_number=len(page_books_features),
        )
        current_dir = Path.cwd() / 'pages'
        Path(current_dir).mkdir(parents=True, exist_ok=True)
        index_file_path = Path() / current_dir / f'index{number}.html'        
        with open(index_file_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def get_user_file_path():
     
    parser = argparse.ArgumentParser(
        description='Программа формирует оффлайн-библиотеку',               
    )
    parser.add_argument('-f', '--json_file', default='books.json', help='Имя json-файла')
    
    args = parser.parse_args()
    return args.json_file