import requests
import os
import time

from modules.ImageParser.PinterestParser import PinterestParser

class ImageDownloader:
    _path: str

    def __init__(self, path: str):
        self._path = path

    def start_download(self):
        url = parser.get_image_url()
        while (url != None):
            self._upload_image(url)
            time.sleep(1)
            url = parser.get_image_url()

    def _upload_image(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            folder_path = os.path.join('images', str(self._path))
            os.makedirs(folder_path, exist_ok=True)

            filename = os.path.join(folder_path, f'image_{
                len(os.listdir(folder_path))}.jpg')

            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Ошибка при загрузке изображения {url}")
            print(response.status_code)


if __name__ == "__main__":
    parser = PinterestParser(debug=True)

    parser.parse_image_urls(
        promt=[
            "anime",
            "nekomimi"
        ]
    )

    imgDownloader = ImageDownloader("test")
    imgDownloader.start_download()