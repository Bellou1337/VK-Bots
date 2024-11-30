import time
import re
import requests
from requests.exceptions import RequestException
from .BaseParser import BaseParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from queue import Queue
from bs4 import BeautifulSoup


class PinterestParser(BaseParser):
    _search_url = "https://ru.pinterest.com/search/pins?q="
    _website = "https://ru.pinterest.com"

    def __init__(self, promt: list[str] = ..., iter=1) -> None:
        self.iter = iter
        super().__init__(promt)

    def _parse_image_urls(self, promt: list[str], num_similar_photos: int = 5,num_main_images: int = 5):
        search_url = self._search_url + "%20".join(promt)
        res = set()
        
        options = webdriver.EdgeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        if self._debug:
            options.add_argument('--headless')

        driver = webdriver.Edge(options=options)

        try:
            driver.get(search_url)
            wait = WebDriverWait(driver, 60)
            wait.until(lambda x: any([
                len(x.find_elements(By.TAG_NAME, 'img')) > 0,
                len(x.find_elements(By.CSS_SELECTOR,
                    'div[data-testid="pin"]')) > 0,
                len(x.find_elements(By.CSS_SELECTOR,
                    'div[role="listitem"]')) > 0,
            ]))

        except Exception as e:
            print(f"Ошибка при открытии страницы/ не нашёл нужный тег: {e}")
            return

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        image_queue = Queue()

        wrong_data_ids = [
            'inp-perf-pinType-storyPin',
            'inp-perf-pinType-video'
        ]

        for a in soup.find_all('a', href=True):

            if len(res) >= num_main_images:
                break

            if "/pin/" in str(a) and not self._website + str(a.get('href')) in res:

                fl = True

                for data_id in wrong_data_ids:
                    el = a.find('div', {'data-test-id': data_id})
                    if el:
                        fl = False
                    else:
                        if not a.find('img'):
                            fl = False

                if not fl:
                    continue

                if self._single_photo_search(
                        self._website + str(a.get('href')), driver):

                    res.add(self._website + str(a.get('href')))
                    image_queue.put(self._website + str(a.get('href')))

        original_window = driver.current_window_handle

        while not image_queue.empty():
            url = image_queue.get()

            try:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(url)

            except NoSuchWindowException:
                if original_window in driver.window_handles:
                    driver.switch_to.window(original_window)
                continue

            try:
                driver.find_element(By.TAG_NAME, "html").send_keys(Keys.END)
                WebDriverWait(driver, 30).until(
                    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))

            except TimeoutException as e:
                driver.close()
                if original_window in driver.window_handles:
                    driver.switch_to.window(original_window)
                print(f"Ошибка ожидания драйвера: {e}")
                continue

            html = driver.find_element(By.TAG_NAME, "html")
            html.send_keys(Keys.END)

            additional_soup = BeautifulSoup(driver.page_source, 'html.parser')

            skip_first_img: bool = True
            mixing_counter: int = 3
            stop_searching: bool = False

            for a in additional_soup.find_all('a', href=True):

                if "/pin/" in str(a) and not self._website + str(a.get('href')) in res:

                    fl = True

                    for data_id in wrong_data_ids:
                        el = a.find('div', {'data-test-id': data_id})
                        if el:
                            fl = False
                        else:
                            if not a.find('img'):
                                fl = False

                    if not fl:
                        continue

                    if skip_first_img:
                        skip_first_img = False
                        continue

                    url = self._website + str(a.get('href'))

                    valid_image = self._single_photo_search(url, driver)

                    if valid_image:
                        res.add(url)

                    if len(res) >= num_similar_photos + num_main_images:
                        stop_searching = True
                        break

                    if mixing_counter > 0 and valid_image:
                        image_queue.put(url)
                        mixing_counter -= 1

            driver.close()
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)

            if stop_searching:
                break

        driver.quit()

    def _single_photo_search(self, url: str, driver: webdriver.Edge) -> bool:

        original_window = driver.current_window_handle

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

        try:
            WebDriverWait(driver, 30).until(
                expected_conditions.presence_of_element_located((By.TAG_NAME, 'img')))

        except TimeoutException as e:
            driver.close()
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)
            print(f"Ошибка ожидания драйвера: {e}")
            return False

        try:

            img = driver.find_element(By.TAG_NAME, "img")
            img_url = img.get_attribute('src')
            original_url = re.sub(
                r"/\d+x/", "/originals/", img_url, count=1)

            response = requests.head(original_url, timeout=10)
            if response.status_code == 200:
                self._urls.append(original_url)
                driver.close()
                if original_window in driver.window_handles:
                    driver.switch_to.window(original_window)
                return True

            driver.close()
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)
            return False

        except RequestException as e:
            driver.close()
            if original_window in driver.window_handles:
                driver.switch_to.window(original_window)

            print(f"Ошибка при получении изображения: {e}")
            return False
