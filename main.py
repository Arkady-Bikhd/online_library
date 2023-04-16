import requests
from pathlib import Path
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename



def main():

    
    fetch_books()   
    

def get_book_title(book_url):

    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_tag_text = title_tag.text.split('::')
    return title_tag_text[0].strip()
    # book_title = title_tag_text[0].strip()
    # book_author = title_tag_text[1].strip()
    # print(f'Заголовок: {book_title}')
    # print(f'Автор: {book_author}')
    #print(soup.f)


def fetch_books():

    book_url = 'https://tululu.org/b'
    text_url = 'https://tululu.org/txt.php?id='
    first_id = 1
    folder = 'books'
    for id in range(10):
        try:
            book_url_id = f'{book_url}{first_id + id}/'
            filename = f'{first_id+id}. {get_book_title(book_url_id)}'
            text_url_id = f'{text_url}{first_id + id}'
            download_txt(text_url_id, filename, folder)
        except HTTPError: 
            print('Такой книги нет')     


def check_for_redirect(response):

    if response.history:
        raise HTTPError


def download_txt(url, filename, folder):

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'{sanitize_filename(filename)}.txt'
    current_dir = Path.cwd() / folder
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path() / current_dir / filename
    with open(filepath, 'wb') as file:
        file.write(response.content)

if __name__ == '__main__':

    main()