import requests
from pathlib import Path


def main():

    book_url = 'https://tululu.org/txt.php?id='
    first_id = 32168
    text_dir = 'books'
    for id in range(10):
        url_id = f'{book_url}{first_id + id}'
        text_file = f'id{id}.txt'
        get_text_file(url_id, text_file, text_dir)    


def get_text_file(url, text_file, text_dir):

    response = requests.get(url)
    response.raise_for_status()
    current_dir = Path.cwd() / text_dir
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    file_name = Path() / current_dir / text_file
    with open(file_name, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':

    main()