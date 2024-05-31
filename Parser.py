from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import URLError
import settings
import asyncio
import aiohttp
from models import db_session, Materials

ROOT = 'https://vlg.saturn.net/'

def get_first_text(iter):
    for item in iter:
        return item.text.strip()

def get_all_text(iter):
    return [item.text.strip() for item in iter]

def get_all_href(iter):
    return [link.get('href') for link in iter]

def get_all_src(iter):
    return [img.get('src') for img in iter]

def fetcher():
    with urlopen(ROOT) as request:
        return request.read()

def parser(html):
    soup = BeautifulSoup(html, 'html.parser')

    for i, div in enumerate(soup.select('div.goods_new_slider_container li')):
        titles = get_first_text(div.select('div.goods_card_link a.goods_card_text.swiper-no-swiping'))
        price = get_first_text(div.select('div.goods_card_price_wrap span.js-price-value'))
        articul = get_first_text(div.select('div.goods_card_articul'))

        print('Название:', titles)
        print('Цена:', price)
        print('Артикул:', articul)
        Item = Materials(titles=titles, articul=articul, price=price)
        db_session.add(Item)
        db_session.commit()



if __name__ == '__main__':
    parser(fetcher())
