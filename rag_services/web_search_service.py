import asyncio

from duckduckgo_search import DDGS
from typing import List
import time, random
import logging
from bs4 import BeautifulSoup
from unidecode import unidecode
import requests
from urllib.request import urlopen
from langchain_community.document_loaders import WebBaseLoader

from rag_services.enahnce_and_clean_data_service import  EnhanceService


class WebScrapService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
    # def __init__(self, term: str):
    #    when:1d"

    def google_search(self, term):
        try:
            formatted_term = unidecode(term).replace(' ', '+')
            url = f"https://news.google.com/rss/search?q={formatted_term}&when:1d"
            client = urlopen(url)
            xml_page = client.read()
            client.close()

            soup = BeautifulSoup(xml_page, "xml")
            urls = [news.link.text for news in soup.findAll("item")]
            return urls
        except Exception as e:
            logging.error(f"GoogleNewsSearch error: {e}")
            return []

    def resolve_redirect(self, url):
        try:
            response = requests.get(url, headers=self.headers, allow_redirects=True, timeout=5)
            if response.status_code == 200:
                return response.url
        except requests.exceptions.RequestException as e:
            logging.warning(f"Redirect resolution failed: {e}")
        return None

    def yahoo_search(self, query, max_results=5):
        try:

            url = f"https://search.yahoo.com/search?p={unidecode(query).replace(' ', '+')}"
            response = requests.get(url, headers=self.headers, allow_redirects=True)
            soup = BeautifulSoup(response.text, "html.parser")
            links = []
            for div in soup.find_all("div", class_="compTitle"):
                a_tag = div.find("a", href=True)
                if a_tag:
                    raw_href = a_tag["href"]
                    if raw_href.startswith("http"):
                        final_url = self.resolve_redirect(raw_href)
                        if final_url and final_url.startswith("http"):
                            links.append(final_url)
                if len(links) >= max_results:
                    break
            return links
        except Exception as e:
            logging.error(f"YahooSearch error: {e}")
            return []


    def search_duckduckgo_urls(self, query: str, num_results: int = 5, retries: int = 3) -> List[str]:
        urls = []
        try:
            with DDGS() as ddgs:
                for attempt in range(retries):
                    try:
                        print(f" Searching: {query} | Attempt {attempt+1}")
                        time.sleep(random.uniform(0.5, 2.0))
                        results = ddgs.text(query, max_results=num_results)
                        for result in results:
                            url = result.get("href")
                            if url:
                                urls.append(url)
                        print(urls)
                        break
                    except Exception as e:
                        print(f" Retry due to error: {e}")
                        time.sleep(2 + attempt)
        except Exception as final_error:
            print(f"Failed after retries: {final_error}")
        return urls

    async def scrape_urls_with_webbase_loader(self, urls: List[str]) -> List:
        documents = []
        for url in urls:
            try:
                print(f" Scraping: {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        return documents

    async def duckduckgo_search_and_scrape(self, query: str):
        urls = self.search_duckduckgo_urls(query)
        # urls = self.yahoo_search(query)
        # urls = self.google_search(query)
        print(urls)
        docs = await self.scrape_urls_with_webbase_loader(urls)
        # tasks = [asyncio.to_thread(EnhanceService(llm).clean_urls_data_service, doc, query) for doc in docs]
        # documents = await asyncio.gather(*tasks)
        return docs
