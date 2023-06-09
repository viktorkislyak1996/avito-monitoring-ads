import logging
from datetime import datetime
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from starlette import status
from transliterate import translit

logger = logging.getLogger(__name__)


class AvitoAvsScraper:
    """
    The class that allows to scrape Avito advertisements
    based on a specific search query and region

    Args:
        query: The query to scrape.

    Attributes:
        query: The query to scrape.
        domain: The domain name of the site to be parsed.
        headers: The headers for request.
        soup: The BeautifulSoup object.
    """

    domain = "https://www.avito.ru"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "max-age=0",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Sec-Ch-Ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.avito.ru/",
    }

    def __init__(self, query: dict) -> None:
        self.query = query
        self.soup = None

    def __build_url(self) -> str:
        """
        Build the URL by search phrase and region.

        Returns:
            The URL address to scrape avito.
        """
        region = self.query.get("region", "")
        translit_region = translit(region, "ru", reversed=True).lower()
        search_phrase = quote(self.query.get("search_phrase", "").replace(" ", "+"))
        return f"{self.domain}/{translit_region}?q={search_phrase}"

    def __get_content(self) -> BeautifulSoup:
        """
        Get BeautifulSoup content.

        Returns:
            The BeautifulSoup content.
        """
        avito_ads_url = self.__build_url()
        page_content = self.__process_request(avito_ads_url)
        try:
            self.soup = BeautifulSoup(page_content, "lxml")
        except TypeError:
            logger.error(
                "Parser didn't find the total number of ads. "
                "Please check the correctness of the parser"
            )
        else:
            return self.soup

    def get_ads_number(self) -> dict | None:
        """
        Receive the number of ads.

        Returns:
            The dict that contains the number of ads,
            timestamp and query id
        """
        self.__get_content()
        if not self.soup:
            return None

        try:
            text_number = self.soup.find(class_="page-title-count-wQ7pG").text
        except AttributeError:
            logger.error(
                "Parses didn't find the total number of ads. "
                "Please check the correctness of the parser"
            )
            return

        try:
            quantity = int("".join(text_number.strip().split()))
        except ValueError:
            logging.error(
                "Error during receiving the number of ads. Please check "
                "if the URL is correct or try to make request later."
            )
            return

        timestamp = datetime.now()
        result = {
            "query_id": self.query.get("_id"),
            "quantity": quantity,
            "timestamp": timestamp,
        }
        return result

    def get_top_ads(self) -> list[dict | None] | None:
        """
        Receive top 5 ads.

        Returns:
            The list of dicts that contain title, description,
            price, place and timestamp info.
        """
        self.__get_content()
        if not self.soup:
            return None

        result = []
        elements = self.soup.select(".iva-item-content-rejJg")[:5]
        for el in elements:
            try:
                title = el.find(class_="iva-item-titleStep-pdebR").text
                description = el.find(class_="iva-item-descriptionStep-C0ty1").text
                price = el.find(class_="iva-item-priceStep-uq2CQ").text
                place = el.find(class_="geo-root-zPwRk").text
                timestamp = el.find(class_="iva-item-dateInfoStep-_acjp").text
            except AttributeError:
                logger.error(
                    "Error during parsing ads. "
                    "Please check the correctness of the parser"
                )
                continue

            data = {
                "title": title,
                "description": description,
                "price": price,
                "place": place,
                "timestamp": timestamp,
            }
            result.append(data)
        return result

    def __process_request(self, url: str) -> str:
        """
        Makes a request by URL and returns the content.

        Args:
            url: The URL to make request.

        Returns:
            The page content.

        """
        try:
            response = requests.get(url, headers=self.headers)
        except Exception as e:
            logger.error(f"Error during making request to Avito: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error during making request to Avito. Please try again later.",
            )

        if response.status_code >= 500:
            # logger.error("Avito server error occurred")
            raise HTTPException(
                status_code=response.status_code,
                detail="Avito server error occurred.",
            )
        elif 400 <= response.status_code < 500:
            # logger.error("Error during making request to Avito")
            raise HTTPException(
                status_code=response.status_code,
                detail="Error during making request to Avito.",
            )
        return response.text


if __name__ == "__main__":
    test_query = {
        "_id": "647f1fe1a18086e2dab6ec0c",
        "search_phrase": "iPhone 14 Pro Max",
        "region": "Москва",
    }
    scraper = AvitoAvsScraper(test_query)
    top_ads = scraper.get_top_ads()
