import requests
from pathlib import Path
from requests.exceptions import HTTPError, ConnectionError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
from retry import retry
from main import check_for_redirect, parse_book_page, download_txt, download_image, get_book_html
import json


def main():
    
    
    #pages_ids = #get_initial_args()    
    books_folder = 'books'
    images_folder = 'images'
    page_start = 0
    page_end = 2
    if not page_start:
        page_start = 1
        
    books_feateres = list()   
    for page_id in range(page_start, page_end+1):
        try:
            books_feateres.append(fetch_books(page_id, books_folder, images_folder))                                  
        except HTTPError: 
            pass
        except ConnectionError:
            print('Ошибка соединения')            
    create_books_json(books_feateres)         


def get_genre_html(page_id, genre_id='l55'):

    genre_url = f'https://tululu.org/{genre_id}/{page_id}/'
    response = requests.get(genre_url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')

def parse_genre_page(soup: BeautifulSoup):    
    
    book_ids = list()    
    for find_div in soup.find_all('div', class_='bookimage'):
        for tag_a in find_div:
            book_ids.append(''.join(filter(str.isdigit, tag_a.get('href'))))
    return book_ids           


def create_books_json(books_feateres):

    book_feateres_json = json.dumps(books_feateres, ensure_ascii=False)
    with open("books.json", "w") as json_file:
        json_file.write(book_feateres_json)


@retry(ConnectionError, tries=3, delay=1, backoff=5)
def fetch_books(page_id, books_folder, images_folder):
    book_ids = parse_genre_page(get_genre_html(page_id))
    page_book_feateres = list()           
    for book_id in book_ids:        
        book_feateres = parse_book_page(get_book_html(book_id))
        download_txt(book_id, book_feateres['book_title'], books_folder)
        download_image(book_id, book_feateres['image_src'], images_folder)
        book_feateres['book_path'] = f'{books_folder}/{book_feateres["book_title"]}.txt'       
        page_book_feateres.append(book_feateres)          
    return page_book_feateres


if __name__ == '__main__':

    main()