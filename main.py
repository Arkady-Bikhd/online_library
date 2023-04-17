import requests
from pathlib import Path
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse



def main():
    
    fetch_books()   
    

def get_book_html(id):

    book_url = f'https://tululu.org/b{id}/'    
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, 'lxml')


def parse_book_page(soup):

    book_features = dict()
    title_tag = soup.find('h1')
    title_tag_text = title_tag.text.split('::')
    comments = soup.find_all('div', class_='texts')
    genres = soup.find('span', class_='d_book').find_all('a')
    book_features['book_title'] = title_tag_text[0].strip()
    book_features['book_author'] = title_tag_text[1].strip()
    book_features['book_comments'] = [comment.find('span').text for comment in comments]
    book_features['book_genres'] = [genre.text for genre in genres]
    book_features['image_src'] = soup.find('div', class_='bookimage').find('img')['src']
    return book_features    


def fetch_books():

    book_ids = get_initial_args()
    books_folder = 'books'
    images_folder = 'images'
    for id in range(book_ids[0], book_ids[1]+1):
        try:
            book_feateres = parse_book_page(get_book_html(id))
            download_txt(id, book_feateres['book_title'], books_folder)
            download_image(id, book_feateres['image_src'], images_folder)
            print_book_features(book_feateres)
        except HTTPError: 
            print('Книга с таким номером не найдена')     


def check_for_redirect(response):

    if response.history:
        raise HTTPError


def download_txt(id, book_title, folder):

    text_url = 'https://tululu.org/txt.php'
    payload = {'id': id}
    response = requests.get(text_url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'{id}. {sanitize_filename(book_title)}.txt'
    current_dir = Path.cwd() / folder
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path() / current_dir / filename
    with open(filepath, 'wb') as file:
        file.write(response.content)

def download_image(id, image_src, folder):

    filename = image_src.split('/')[-1]
    book_url = f'https://tululu.org/b{id}'
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
    return args.start_id, args.end_id
    

if __name__ == '__main__':

    main()