import logging
from datetime import datetime
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from transliterate import translit

from core.database import counter_collection

logger = logging.getLogger(__name__)


class AvitoAvsScraper:
    """
    The class that allows to scrape Avito advertisements
    based on a specific search query and region

    Args:
        avs_url (str): The url to scrape.

    Attributes:
        avs_url (str): The url to scrape.
    """

    domain = "https://www.avito.ru"

    def __init__(self, query: dict) -> None:
        self.query = query

    def build_url(self) -> str:
        region = self.query.get("region", "")
        translit_region = translit(region, "ru", reversed=True).lower()
        search_phrase = quote(self.query.get("search_phrase", "").replace(" ", "+"))
        return f"{self.domain}/{translit_region}?q={search_phrase}"

    def get_content(self) -> BeautifulSoup:
        avito_ads_url = self.build_url()
        response = self.process_request(avito_ads_url)
        page_content = response.text
        soup = BeautifulSoup(page_content, "lxml")
        return soup

    def get_ads_number(self, soup: BeautifulSoup) -> None:
        text_number = soup.find(class_="page-title-count-wQ7pG").text
        try:
            quantity = int("".join(text_number.strip().split()))
        except ValueError:
            logging.error(
                "Error during receiving the number of ads. Please check "
                "if the url is correct or try to make request later."
            )
        else:
            timestamp = datetime.now()
            result = {
                "query_id": self.query.get("_id"),
                "quantity": quantity,
                "timestamp": timestamp,
            }
            self.write_to_database(result)

    def write_to_database(self, data: dict) -> None:
        counter_collection.insert_one(data)

    def process_request(self, url: str):
        try:
            response = requests.get(url)
        except Exception as e:
            logger.error(f"{e}")
        else:
            return response
