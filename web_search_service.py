from duckduckgo_search import DDGS
from typing import List
import time, random

from langchain_community.document_loaders import WebBaseLoader


class WebScrapService:
    def search_duckduckgo_urls(self, query: str, num_results: int = 5, retries: int = 3) -> List[str]:
        urls = []
        try:
            with DDGS() as ddgs:
                for attempt in range(retries):
                    try:
                        print(f"🔍 Searching: {query} | Attempt {attempt+1}")
                        time.sleep(random.uniform(0.5, 2.0))
                        results = ddgs.text(query, max_results=num_results)
                        for result in results:
                            url = result.get("href")
                            if url:
                                urls.append(url)
                        print(urls)
                        break
                    except Exception as e:
                        print(f"⚠️ Retry due to error: {e}")
                        time.sleep(2 + attempt)
        except Exception as final_error:
            print(f"Failed after retries: {final_error}")
        return urls
    
    async def scrape_urls_with_webbase_loader(self, urls: List[str]) -> List:
        documents = []
        for url in urls:
            try:
                print(f"🌐 Scraping: {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")
        return documents
    
    async def duckduckgo_search_and_scrape(self, query: str, num_results: int = 5):
        urls = self.search_duckduckgo_urls(query, num_results)
        documents = await self.scrape_urls_with_webbase_loader(urls)
        return documents