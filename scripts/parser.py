"""
parser.py

Модуль для парсинга статей с новостного сайта RIA.ru по заданной категории.
Использует Selenium + webdriver-manager для автоматического управления драйвером.
Извлекает заголовок, ссылку, количество просмотров и теги для каждой статьи.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_driver():
    """
    Настраивает и возвращает объект Chrome WebDriver.
    """
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--start-minimized")
    # options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    logging.info("Инициализация драйвера Chrome")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_category(url, max_articles=200):
    """
    Парсит заданную категорию новостей на ria.ru.

    Args:
        url (str): Ссылка на категорию новостей.
        max_articles (int): Максимальное количество статей для парсинга.

    Returns:
        dict: Словарь с данными по каждой статье (ключ — ссылка).
    """
    driver = setup_driver()
    driver.get(url)
    time.sleep(2)

    articles = {}
    collected = 0
    logging.info(f"Парсинг категории: {url}")

    while collected < max_articles:
        items = driver.find_elements(By.CLASS_NAME, "list-item")

        for item in items[len(articles):]:
            try:
                title_tag = item.find_element(By.CLASS_NAME, "list-item__title")
                title = title_tag.text
                link = title_tag.get_attribute("href")

                try:
                    views_block = item.find_element(By.CSS_SELECTOR, 'div.list-item__info-item[data-type="views"]')
                    views_span = views_block.find_element(By.TAG_NAME, "span")
                    views = int(views_span.text.replace(" ", ""))
                except Exception as e:
                    logging.warning(f"Не удалось получить просмотры: {e}")
                    views = None

                try:
                    tags_block = item.find_element(By.CLASS_NAME, "list-item__tags")
                    tags = [t.text for t in tags_block.find_elements(By.TAG_NAME, "a")]
                except:
                    tags = []

                articles[link] = {
                    "title": title,
                    "views": views,
                    "tags": tags,
                }
                collected += 1

                logging.info(f"[{collected}/{max_articles}] {title} ({views} views)")

                if collected >= max_articles:
                    break
            except Exception as e:
                logging.warning(f"Ошибка при обработке статьи: {e}")
                continue

        if collected < max_articles:
            try:
                more_button = driver.find_element(By.CLASS_NAME, "list-more")
                driver.execute_script("arguments[0].click();", more_button)
                logging.info("Нажата кнопка 'Показать ещё'")
                time.sleep(2)
            except Exception as e:
                logging.warning("Не удалось нажать кнопку 'Показать ещё': %s", e)
                break

    driver.quit()
    logging.info(f"Готово. Собрано статей: {len(articles)}")
    return articles
