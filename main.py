import requests
from pathlib import Path


def main():

    book_url = 'https://tululu.org/txt.php?id=32168'
    response = requests.get(book_url)
    response.raise_for_status()
    filename = 'Пески Марса.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)


def get_image(url, image_file, image_dir):

    response = requests.get(url)
    response.raise_for_status()
    current_dir = Path.cwd() / image_dir
    Path(current_dir).mkdir(parents=True, exist_ok=True)
    file_name = Path() / current_dir / image_file
    with open(file_name, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':

    main()