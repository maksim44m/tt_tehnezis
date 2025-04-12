import asyncio
import re
from typing import Tuple

from parsel import Selector
from aiohttp import ClientSession, ClientTimeout

from db import get_all_id_url_xpath, update_avg_price
from config import headers


async def get_data_from_site(session: ClientSession,
                             item: Tuple[int, str, str]) -> Tuple[int, float]:
    id_, url, xpath = item
    # выгрузка html
    timeout = ClientTimeout(total=10)
    try:
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            content = await resp.text()
        selector = Selector(text=content)
        prices_from_url = []
        # обработка полученных значений цены
        for raw_price in selector.xpath(xpath):
            price = re.sub(
                r'[^\d.,]', '', str(raw_price)
            ).replace(',', '.')
            if not price:
                continue
            if price.count('.') > 1:
                parts_price = price.split('.')
                price = f"{''.join(parts_price[:-1])}.{parts_price[-1]}"
            prices_from_url.append(round(float(price), 2))
        # если получили цены, то выводим среднее и отдаем
        if prices_from_url:
            avg_price = round(sum(prices_from_url) / len(prices_from_url), 2)
            return id_, avg_price
        else:
            return id_, 0
    except Exception as e:
        print(f'get_data_from_site ERROR {e}')
        return id_, 0


async def run_parser():
    # получение url и xpath из бд + id
    urls_and_xpaths = get_all_id_url_xpath()
    # проход по всем сайтам
    tasks = []
    async with ClientSession() as session:
        for item in urls_and_xpaths:
            tasks.append(asyncio.create_task(get_data_from_site(session, item)))
        result = await asyncio.gather(*tasks)
    update_avg_price(result)

