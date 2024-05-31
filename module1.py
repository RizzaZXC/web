import asyncio
import aiohttp
from bs4 import BeautifulSoup
from models import db_session, Materials  # Импорт неизвестен, но должен быть для работы с вашей базой данных
import time  # Импортируем модуль для измерения времени выполнения

# Ссылка на магазин, который парсим
ROOT = 'https://vlg.saturn.net/'
ITEMS_ROOT = "https://vlg.saturn.net/catalog/Stroymateriali/"

# Максимальное количество одновременных задач
PARALLEL_TASKS = 70
# Семафор для ограничения количества одновременных запросов
MAX_DOWNLOAD_AT_TIME = asyncio.Semaphore(PARALLEL_TASKS)


def get_first_text(iter):
    # Вспомогательная функция для извлечения текста из элементов BS4
    for item in iter:
        return item.text.strip()


async def fetch(session, url):
    # Асинхронная функция для загрузки HTML с URL
    async with MAX_DOWNLOAD_AT_TIME:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Error fetching {url}: {response.status}")
                    return None
        except Exception as e:
            print(f"Exception fetching {url}: {e}")
            return None


def parser_categories(html):
    # Функция для парсинга категорий из корневой страницы
    urls = []
    soup = BeautifulSoup(html, features="lxml")
    for div in soup.select('div.top_menu_catalogBlock a.top_menu_catalogBlock_listBlock_item.swiper-slide'):
        categories = get_first_text(div)
        url = div.get('href')
        if url:
            full_url = ROOT + url
            urls.append(full_url)
            print(f"Category: {categories} ---> URL: {full_url}")
    return urls


async def parser_items(session, url):
    # Асинхронная функция для парсинга товаров из страницы категории
    page_number = 1
    items_url = f"{url}?page={page_number}&per_page=20"
    items_html = await fetch(session, items_url)
    if items_html:
        soup = BeautifulSoup(items_html, features="lxml")
        tasks = []
        item_divs = soup.select('div.catalog_Level2__goods_list__block li.catalog_Level2__goods_list__item')
        if not item_divs:
            print(f"No more items found on {items_url}")
        for i, div in enumerate(item_divs):
            titles = get_first_text(div.select('div.goods_card_link a.goods_card_text.swiper-no-swiping'))
            price = get_first_text(div.select('div.goods_card_price_discount_value span.js-price-value'))
            articul = get_first_text(div.select('div.goods_card_articul span'))
            item_url = div.select_one('div.goods_card_link a.goods_card_text.swiper-no-swiping').get('href')
            if item_url:
                item_url = ROOT + item_url
                tasks.append(fetch_description_and_save(session, titles, articul, price, item_url))
        await asyncio.gather(*tasks)


async def fetch_description_and_save(session, titles, articul, price, url):
    # Асинхронная функция для загрузки описания и сохранения товара в базу данных
    try:
        print(f"Item: {titles}, articul: {articul}, price: {price}")
        print('Название:', titles)
        print('Цена:', price)
        print('Артикул:', articul)
        item = Materials(titles=titles, articul=articul, price=price)
        db_session.add(item)
        db_session.commit()
    except Exception as e:
        print(f"Error reading from {url}: {e}")


async def gather_data():
    # Основная асинхронная функция для сбора данных
    async with aiohttp.ClientSession() as session:
        root_html = await fetch(session, ROOT)
        if root_html:
            category_urls = parser_categories(root_html)
            tasks = []
            for url in category_urls:
                tasks.append(parser_items(session, url))
            await asyncio.gather(*tasks)


# Запускаем основную асинхронную функцию
if __name__ == '__main__':
    start_time = time.time()  # Записываем текущее время для измерения
    asyncio.run(gather_data())  # Запускаем основную асинхронную функцию
    end_time = time.time()  # Записываем время окончания выполнения
    print(f"Execution time: {end_time - start_time} seconds")  # Выводим время выполнения
