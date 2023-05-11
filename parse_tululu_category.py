from pathlib import Path
from requests.exceptions import HTTPError, ConnectionError
from bs4 import BeautifulSoup
import argparse
from retry import retry
from main import parse_book_page, download_txt, download_image, get_html
import json


def main():    
    
    initial_args = get_initial_args()
    dest_folder = initial_args.dest_folder
    books_folder = 'books'
    images_folder = 'images'
    base_url = 'https://tululu.org/'
    books_folder = Path() / dest_folder / books_folder
    images_folder = Path() / dest_folder / images_folder
    end_page = initial_args.end_page
    if not end_page:
        end_page = int(get_html((f'{base_url}l55/{initial_args.start_page}/')).select('.npage')[-1].text)       
    books_features = list()   
    for page_id in range(initial_args.start_page, end_page + 1):
        try:                    
            books_features.append(fetch_books(page_id, books_folder, images_folder, initial_args.skip_txt, initial_args.skip_images, base_url))                                  
        except HTTPError: 
            print('Страница не найдена')
        except ConnectionError:
            print('Ошибка соединения')            
    create_books_json(books_features, initial_args.json_path)         


def parse_genre_page(soup: BeautifulSoup):    
    
    href_selector = '.bookimage a'
    hrefs = soup.select(href_selector)    
    book_ids = [(''.join(filter(str.isdigit, href['href']))) for href in hrefs]
    return book_ids           


def create_books_json(books_features, json_path):    
    
    current_dir = Path.cwd() / json_path
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path() / current_dir / "books.json" 
    json_books_features = list()
    for books in books_features:
        for book in books:
            if book['book_path']:
                json_books_features.append(book)   
   # print(json_books_features)    
    with open(filepath, "w") as json_file:
        json.dump(json_books_features, json_file, ensure_ascii=False)


@retry(ConnectionError, tries=3, delay=1, backoff=5)
def fetch_books(page_id, books_folder, images_folder, skip_txt, skip_images, base_url):
    
    book_ids = parse_genre_page(get_html(f'{base_url}l55/{page_id}/'))
    page_book_features = list()            
    for book_id in book_ids:        
        book_features = parse_book_page(get_html(f'{base_url}b{book_id}/'))
        if not skip_txt:
            if download_txt(book_id, book_features['book_title'], books_folder):
                book_features['book_path'] = f'media/books/{book_features["book_title"]}.txt' 
            else:
                book_features['book_path'] = None
        if not skip_images:
            download_image(book_id, book_features['image_src'], images_folder)
            book_features['image_src'] = f"media/images/{book_features['image_src'].split('/')[2]}"                    
        page_book_features.append(book_features) 
    #print (page_book_features)           
    return page_book_features


def get_initial_args():
     
    parser = argparse.ArgumentParser(
        description='Программа формирует элетронную библиотеку',               
    )
    parser.add_argument('-sp', '--start_page', type=int, help='Номер начальной страницы')
    parser.add_argument('-ep', '--end_page', nargs='?', type=int, help='Номер последней страницы')
    parser.add_argument('-df', '--dest_folder', default='media', help='Путь к каталогу')
    parser.add_argument('-si', '--skip_images', action='store_true', help='Не скачивать картинки')
    parser.add_argument('-st', '--skip_txt', action='store_true', help='Не скачивать книги')
    parser.add_argument('-jp', '--json_path', default='', help='Путь к json-файлу')

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    main()