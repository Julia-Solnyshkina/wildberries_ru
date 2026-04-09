from copy import deepcopy
import scrapy
from scrapy import Request
from w3lib.url import add_or_replace_parameter
from ..constants import *


class WildberriesParser:

    def get_url(self, jo):
        url = PRODUCT_URL.format(sku=jo.get('id', ''))
        return {'url': url}

    def get_article(self, jo):
        return {'article': jo.get('id', '')}

    def get_name(self, jo):
        return {'name': jo.get('name', '')}

    def get_product(self, jo):
        sizes = jo.get('sizes', [])
        for size in sizes:
            price = size.get('price')
            stocks = size.get('stocks', [])
            if price and price.get('product') and stocks:
                product = size
                return product

    def get_price(self, product):
        return {'price': product.get('price')['product'] / 100}

    def get_seller_info(self, jo):
        seller_name = jo.get('supplier', '')
        seller_url = SELLER_URL.format(seller_id=jo.get('supplierId'))
        return {'seller_name': seller_name,
                'seller_url': seller_url}

    def get_sizes(self, jo):
        sizes = jo.get('sizes', [])
        sizes = [size.get('origName', '') for size in sizes if size.get('name')]
        return {'sizes': ', '.join(sizes)}

    def get_quantity(self, product):
        quantity = product.get('qty', 0)
        return {'quantity': quantity}

    def get_reviews(self, jo):
        review = jo.get('reviewRating', 0.0)
        reviews_count = int(jo.get('feedbacks', 0))
        return {'reviews_count': reviews_count, 'rating': review}

    def split_sku(self, sku: str):
        """
        Разбивает SKU на части
        """
        return sku[:-5], sku[:-3]

    def get_basket_number(self, sku_prefix: int):
        """
        Определяет номер basket (CDN сервера) по диапазону SKU.
        """
        for index, threshold in enumerate(WB_BASKET_RANGES, start=1):
            if sku_prefix <= threshold:
                return str(index).zfill(2)

        # fallback (если SKU больше всех диапазонов)
        return str(len(WB_BASKET_RANGES) + 1).zfill(2)

    def get_wb_card_url(self, sku):
        """
        Формирует URL card.json товара Wildberries.
        """
        sku = str(sku)
        sku_vol, sku_part = self.split_sku(sku)
        basket = self.get_basket_number(int(sku_vol))
        return (
            f"https://basket-{basket}.wbbasket.ru/"
            f"vol{sku_vol}/part{sku_part}/{sku}/info/ru/card.json"
        )

    def get_metadata(self, jo):
        metadata = {}
        characteristics = {}
        metadata['description'] = jo.get('description', '')
        for option in jo.get('options', []):
            characteristics[option['name']] = option.get('value', '')

        country = characteristics.get('Страна производства', '').lower()
        if country in ["россия", "рф", "российская федерация", "ru"]:
            metadata['country'] = "Россия"
        else:
            metadata['country'] = country

        metadata['characteristics'] = "\n".join(f"{key}:  {value}" for key, value in characteristics.items())
        return metadata

    def get_images(self, jo=None, sku=None):
        images = []
        sku = str(sku)
        photo_count = jo.get('media', {}).get('photo_count', 0)
        sku_vol, sku_part = self.split_sku(sku)
        basket = self.get_basket_number(int(sku_vol))
        count = photo_count if photo_count > 0 else 1
        for i in range(1, count + 1):
            photo_url = IMG_URL.format(
                basket=basket,
                sku=sku,
                sku_without_5=sku_vol,
                sku_without_3=sku_part,
                image_number=i
            )
            images.append(photo_url)
        return {'images': ', '.join(images)}



class WildberriesSpider(scrapy.Spider, WildberriesParser):
    name = "wildberries_ru"
    allowed_domains = ["wildberries.ru", "api-ios.wildberries.ru"]
    source = "https://www.wildberries.ru"
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 2,
        "ROBOTSTXT_OBEY": False,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited_skus = set()

    def start_requests(self):
        for term in SEARCH_TERMS:
            url_search = add_or_replace_parameter(SEARCH_API_URL,'query',term)
            yield Request(
                url=url_search,
                headers=HEADERS,
                callback=self.parse_search,
                cb_kwargs={"page": 1, 'url_search':url_search},
            )


    def parse_search(self, response, **kwargs):
        jo = response.json()
        products = jo.get('products', [])
        for product in products:
            sku = product.get('id', '')
            if sku not in self.visited_skus:
                self.visited_skus.add(sku)
                url_product = add_or_replace_parameter(PRODUCT_API_URL,'nm',sku)
                yield Request(url=url_product,
                              headers=HEADERS,
                              callback=self.parse_product,
                              dont_filter=True)

        if len(products)>=100:
            kwargs['page'] += 1
            url_search = add_or_replace_parameter(kwargs['url_search'], 'page', kwargs['page'])
            yield Request(
                url=url_search,
                headers=HEADERS,
                callback=self.parse_search,
                cb_kwargs=deepcopy(kwargs),
            )


    def parse_product(self, response, **kwargs):
        products_json = response.json()
        for jo in products_json.get('products', []):
            result = {}
            product = self.get_product(jo)
            result.update(self.get_url(jo))
            result.update(self.get_article(jo))
            result.update(self.get_name(jo))
            result.update(self.get_price(product))
            result.update(self.get_seller_info(jo))
            result.update(self.get_sizes(jo))
            result.update(self.get_quantity(product))
            result.update(self.get_reviews(jo))

            wb_card_url = self.get_wb_card_url(result['article'])
            yield Request(url=wb_card_url,
                          callback=self.parse_card,
                          cb_kwargs={'result': result},
                          dont_filter=True)


    def parse_card(self, response, **kwargs):
        result = kwargs['result']
        jo = response.json()
        result.update(self.get_metadata(jo))
        result.update(self.get_images(jo, str(result['article'])))
        yield result