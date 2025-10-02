import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote


class WildberriesParser:
    def __init__(self):
        self.base_url = "https://www.wildberries.ru"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_products(self, query, max_products=50):
        """Поиск товаров по запросу"""
        try:
            # Кодируем запрос для URL
            encoded_query = quote(query)
            search_url = f"{self.base_url}/catalog/0/search.aspx?search={encoded_query}"

            print(f"Поиск по URL: {search_url}")

            response = self.session.get(search_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Ищем карточки товаров
            products = self._parse_product_cards(soup)

            # Ограничиваем количество товаров
            return products[:max_products]

        except Exception as e:
            print(f"Ошибка при поиске товаров: {e}")
            return []

    def _parse_product_cards(self, soup):
        """Парсинг карточек товаров"""
        products = []

        # Несколько возможных селекторов для карточек товаров
        selectors = [
            '.product-card',
            '.catalog-product',
            '[data-card]',
            '.card-product'
        ]

        for selector in selectors:
            product_cards = soup.select(selector)
            if product_cards:
                print(f"Найдено карточек товаров: {len(product_cards)}")
                break

        for card in product_cards:
            try:
                product = self._parse_single_product(card)
                if product and product.get('name') and product.get('price'):
                    products.append(product)
            except Exception as e:
                print(f"Ошибка при парсинге карточки: {e}")
                continue

        return products

    def _parse_single_product(self, card):
        """Парсинг отдельной карточки товара"""
        product = {}

        # Название товара
        name_selectors = [
            '.product-card__name',
            '.goods-name',
            '.catalog-product__name',
            '.card-product__name'
        ]

        for selector in name_selectors:
            name_elem = card.select_one(selector)
            if name_elem:
                product['name'] = name_elem.get_text(strip=True)
                break

        # Цена
        price_selectors = [
            '.price__lower-price',
            '.lower-price',
            '.product-card__price',
            '.catalog-product__price'
        ]

        for selector in price_selectors:
            price_elem = card.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Очищаем цену от лишних символов
                price = self._clean_price(price_text)
                if price:
                    product['price'] = price
                    break

        # Ссылка на товар
        link_selectors = [
            'a.product-card__link',
            'a.catalog-product__link',
            'a[href*="/catalog/"]'
        ]

        for selector in link_selectors:
            link_elem = card.select_one(selector)
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    product['url'] = self.base_url + href
                else:
                    product['url'] = href
                break

        # Бренд (из названия или отдельного поля)
        if 'name' in product:
            product['brand'] = self._extract_brand(product['name'])

        # Рейтинг
        rating_elem = card.select_one('.product-card__rating, .stars, .rating')
        if rating_elem:
            product['rating'] = rating_elem.get_text(strip=True)

        # Количество отзывов
        reviews_elem = card.select_one('.product-card__count, .review-count')
        if reviews_elem:
            product['reviews_count'] = reviews_elem.get_text(strip=True)

        return product

    def _clean_price(self, price_text):
        """Очистка цены от лишних символов"""
        try:
            # Удаляем все символы кроме цифр
            cleaned = ''.join(filter(str.isdigit, price_text))
            return int(cleaned) if cleaned else None
        except:
            return None

    def _extract_brand(self, product_name):
        """Извлечение бренда из названия товара"""
        # Простая логика - первое слово в названии
        words = product_name.split()
        return words[0] if words else ""
