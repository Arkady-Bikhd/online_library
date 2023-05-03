import requests
from pathlib import Path
from requests.exceptions import HTTPError, ConnectionError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
from retry import retry


@retry(ConnectionError, tries=3, delay=1, backoff=5)
def fetch_book(book_id, books_folder, images_folder):
    book_feateres = parse_book_page(get_html(book_id=book_id))
    download_txt(book_id, book_feateres['book_title'], books_folder)
    download_image(book_id, book_feateres['image_src'], images_folder)
    print_book_features(book_feateres)


def main():
    
    book_ids = get_initial_args()    
    books_folder = 'books'
    images_folder = 'images'    
    for book_id in range(book_ids.start_id, book_ids.end_id+1):
        try:
            fetch_book(book_id, books_folder, images_folder)
        except HTTPError: 
            print('Книга с таким номером не найдена')
        except ConnectionError:
            print('Ошибка соединения')               


def url_formation(book_id=None, page_id=None, genre_id='l55'):
    
    url = 'https://tululu.org/'
    if book_id:
        url = f'{url}b{book_id}/'
    if page_id:
        url = f'{url}{genre_id}/{page_id}/'


def get_html(book_id=None, page_id=None, genre_id='l55'):
    
    url = url_formation(book_id=book_id, page_id=page_id, genre_id=genre_id)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def parse_book_page(soup):
    
    title_tag = soup.select_one('h1')
    title_tag_text = title_tag.text.split('::')
    comments = soup.select('.texts span')
    genres = soup.select('.d_book a')
    book_features = {
        'book_title':  title_tag_text[0].strip(),
        'book_author': title_tag_text[1].strip(),
        'book_comments': [comment.text for comment in comments],
        'book_genres': [genre.text for genre in genres], 
        'image_src': soup.select_one('.bookimage img')['src'],
    }    
    return book_features    


def check_for_redirect(response):

    if response.history:
       raise HTTPError
     


def download_txt(book_id, book_title, folder):

    text_url = 'https://tululu.org/txt.php'
    payload = {'id': book_id}
    response = requests.get(text_url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'{sanitize_filename(book_title)}.txt'
    current_dir = Path.cwd() / folder
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path() / current_dir / filename
    with open(filepath, 'wb') as file:
        file.write(response.content)

def download_image(book_id, image_src, folder):

    filename = image_src.split('/')[-1]
    book_url = f'https://tululu.org/b{book_id}'
    image_url = urljoin(book_url, image_src)
    response = requests.get(image_url)
    response.raise_for_status()
    current_dir = Path.cwd() / folder
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path() / current_dir / filename
    with open(filepath, 'wb') as file:
        file.write(response.content)
    
    
def print_book_features(book_features):

    print(f'Автор: {book_features["book_author"]}')
    print(f'Название: {book_features["book_title"]}')
    print(f'Жанр: {book_features["book_genres"]}')
    print('Комментарии')
    for comment in book_features["book_comments"]:
        print(comment)    


def get_initial_args():
     
    parser = argparse.ArgumentParser(
        description='Программа формирует элетронную библиотеку',               
    )
    parser.add_argument('start_id', type=int, help='Номер начальной книги')
    parser.add_argument('end_id', type=int, help='Номер последней книги')
    args = parser.parse_args()
    return args
    

if __name__ == '__main__':

    main()