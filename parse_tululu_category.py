from pathlib import Path
from requests.exceptions import HTTPError, ConnectionError
from bs4 import BeautifulSoup
import argparse
from retry import retry
from main import parse_book_page, download_txt, download_image, get_html, url_formation
import json


def main():    
    
    initial_args = get_initial_args()
    dest_folder = initial_args.dest_folder
    books_folder = 'books'
    images_folder = 'images'
    if dest_folder:
        books_folder = Path() / dest_folder / books_folder
        images_folder = Path() / dest_folder / images_folder
    end_page = initial_args.end_page
    if not end_page:
        end_page = int(get_html(url_formation(page_id=initial_args.start_page)).select('.npage')[-1].text)       
    books_feateres = list()   
    for page_id in range(initial_args.start_page, end_page + 1):
        try:                    
            books_feateres.append(fetch_books(page_id, books_folder, images_folder, initial_args.skip_txt, initial_args.skip_images))                                  
        except HTTPError: 
            print('Страница не найдена')
        except ConnectionError:
            print('Ошибка соединения')            
    create_books_json(books_feateres, initial_args.json_path)         


def parse_genre_page(soup: BeautifulSoup):    
    
    href_selector = '.bookimage a'
    hrefs = soup.select(href_selector)    
    book_ids = [(''.join(filter(str.isdigit, href['href']))) for href in hrefs]
    return book_ids           


def create_books_json(books_feateres, json_path):    
    
    current_dir = Path.cwd() / json_path
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path() / current_dir / "books.json"    
    with open(filepath, "w") as json_file:
        json.dump(books_feateres, json_file, ensure_ascii=False)


@retry(ConnectionError, tries=3, delay=1, backoff=5)
def fetch_books(page_id, books_folder, images_folder, skip_txt, skip_images):
    book_ids = parse_genre_page(get_html(url_formation(page_id=page_id)))
    page_book_feateres = list()           
    for book_id in book_ids:        
        book_feateres = parse_book_page(get_html(url_formation(book_id=book_id)))
        if not skip_txt:
            download_txt(book_id, book_feateres['book_title'], books_folder)
            book_feateres['book_path'] = f'{books_folder}/{book_feateres["book_title"]}.txt' 
        if not skip_images:
            download_image(book_id, book_feateres['image_src'], images_folder)                   
        page_book_feateres.append(book_feateres)          
    return page_book_feateres


def get_initial_args():
     
    parser = argparse.ArgumentParser(
        description='Программа формирует элетронную библиотеку',               
    )
    parser.add_argument('-sp', '--start_page', type=int, help='Номер начальной страницы')
    parser.add_argument('-ep', '--end_page', nargs='?', type=int, help='Номер последней страницы')
    parser.add_argument('-df', '--dest_folder', nargs='?', help='Путь к каталогу')
    parser.add_argument('-si', '--skip_images', action='store_true', help='Не скачивать картинки')
    parser.add_argument('-st', '--skip_txt', action='store_true', help='Не скачивать книги')
    parser.add_argument('-jp', '--json_path', default='', help='Путь к json-файлу')

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    main()