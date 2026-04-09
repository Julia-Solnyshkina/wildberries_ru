SEARCH_TERMS = [
    'пальто из натуральной шерсти'
]

HEADERS = {
    'Host': 'api-ios.wildberries.ru',
    'User-Agent': 'Wildberries/7.5.4000 (RU.WILDBERRIES.MOBILEAPP; build:16316863; iOS 26.2.1) Alamofire/5.9.1',
    'Devicename': 'iOS, iPhone17,1',
    'Wb-Applanguage': 'ru',
    'Devicetoken': '0133f9906e6638c419b9fab380b35de8aacc6423a822e812cabf64078b45ea6a',
    'Site-Locale': 'ru',
    'Wb-Appreferer': 'CatalogProductsVC',
    'Priority': 'u=3, i',
    'Deviceid': '22AC272950704B4B853F675E70D7B36C',
    'X-Clientinfo': 'appType=64;curr=rub;spp=40;dest=-1257786;lang=ru;locale=ru;hide_dtype=11;hide_vflags=4294967296',
    'Wb-Appversion': '754',
    'Accept-Language': 'ru-BY;q=1.0, en-GB;q=0.9',
    'Wb-Apptype': 'ios',
    'Accept': '*/*',
    'X-Queryid': 'qid878001163083407344620260324140104',
}


SEARCH_API_URL = 'https://api-ios.wildberries.ru/__internal/search/exactmatch/ru/common/v14/search?appType=64&curr=rub&dest=-1198055&lang=ru&page=1&resultset=catalog'
PRODUCT_API_URL = 'https://api-ios.wildberries.ru/__internal/card/cards/v4/detail?appType=64&curr=rub&dest=-1198055&lang=ru&locale=ru'

SELLER_URL = 'https://www.wildberries.ru/seller/{seller_id}'
PRODUCT_URL = 'https://www.wildberries.ru/catalog/{sku}/detail.aspx'
VARIANTS_API = 'https://basket-{basket}.wbbasket.ru/vol{sku_without_last_5}/part{sku_without_last_3}/{sku}/info/ru/card.json'
IMG_URL = 'https://basket-{basket}.wbbasket.ru/vol{sku_without_5}/part{sku_without_3}/{sku}/images/big/{image_number}.webp'

WB_BASKET_RANGES = [
    143, 287, 431, 719, 1007, 1061, 1115, 1169, 1313, 1601,
    1655, 1919, 2045, 2189, 2405, 2621, 2837, 3053, 3269, 3485,
    3701, 3917, 4133, 4349, 4565, 4877, 5189, 5501, 5813, 6125,
    6437, 6749, 7061, 7373, 7685, 7997, 8309, 8741, 9173, 9605
]