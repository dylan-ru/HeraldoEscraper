import asyncio
import random
from typing import List, Dict, Optional

from playwright.async_api import async_playwright, Browser, Page

from src.config import (
    USER_AGENT,
    BASE_URL,
    MIN_DELAY,
    MAX_DELAY,
    PAGE_LOAD_TIMEOUT,
    SELECTORS,
)
from src.anti_paywall import remove_paywall, setup_paywall_observer
from src.search import search_news
from src.extractors import extract_search_results, extract_full_article
from src.storage import save_articles


class NewsScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(
            headless=self.headless
        )
        context = await self.browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 720},
        )
        self.page = await context.new_page()
        self.page.set_default_timeout(PAGE_LOAD_TIMEOUT)
        print("[OK] Navegador iniciado")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, "_playwright"):
            await self._playwright.stop()
        print("[OK] Navegador cerrado")

    async def random_delay(self):
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        await asyncio.sleep(delay)

    async def navigate_to_site(self):
        if not self.page:
            raise RuntimeError("Navegador no iniciado. Llame a start() primero.")

        print(f"Navegando a {BASE_URL}...")
        await self.page.goto(BASE_URL, wait_until="domcontentloaded")

        await setup_paywall_observer(self.page)
        await remove_paywall(self.page)

        await self.random_delay()
        print("[OK] Sitio cargado")

    async def search(self, keyword: str) -> bool:
        if not self.page:
            raise RuntimeError("Navegador no iniciado. Llame a start() primero.")

        return await search_news(self.page, keyword)

    async def extract_articles_from_search(self) -> List[Dict]:
        if not self.page:
            raise RuntimeError("Navegador no iniciado. Llame a start() primero.")

        return await extract_search_results(self.page)

    async def scrape_article(self, url: str) -> Optional[Dict]:
        if not self.page:
            raise RuntimeError("Navegador no iniciado. Llame a start() primero.")

        try:
            print(f"Extrayendo artículo: {url}")
            await self.page.goto(url, wait_until="domcontentloaded")

            await remove_paywall(self.page)

            await asyncio.sleep(0.5)

            article = await extract_full_article(self.page)

            await self.random_delay()
            return article

        except Exception as e:
            print(f"Error al extraer artículo {url}: {e}")
            return None

    async def scrape_by_keyword(self,
                                keyword: str,
                                max_articles: Optional[int] = None) -> List[Dict]:
        articles = []

        try:
            await self.navigate_to_site()

            success = await self.search(keyword)
            if not success:
                print("[ERROR] Búsqueda fallida")
                return articles

            await asyncio.sleep(2)

            article_links = await self.extract_articles_from_search()

            if not article_links:
                print("[ERROR] No se encontraron artículos en los resultados")
                return articles

            print(f"Se encontraron {len(article_links)} artículos")

            if max_articles:
                article_links = article_links[:max_articles]

            for i, link in enumerate(article_links, 1):
                print(f"\n[{i}/{len(article_links)}]")

                article = await self.scrape_article(link["article_url"])
                if article:
                    if not article.get("title"):
                        article["title"] = link.get("title")
                    articles.append(article)

            print(f"\n[OK] {len(articles)} artículos extraídos")

        except Exception as e:
            print(f"[ERROR] Extracción fallida: {e}")

        return articles

    async def run(self,
                  keyword: str,
                  max_articles: Optional[int] = None,
                  output_format: str = "csv") -> List[Dict]:
        await self.start()

        try:
            articles = await self.scrape_by_keyword(keyword, max_articles)

            if articles:
                save_articles(articles, output_format)

            return articles

        finally:
            await self.close()


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scraper de Noticias de El Heraldo")
    parser.add_argument("keyword", help="Palabra clave de búsqueda")
    parser.add_argument(
        "-m", "--max",
        type=int,
        default=None,
        help="Número máximo de artículos a extraer"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "sqlite"],
        default="csv",
        help="Formato de salida (default: csv)"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Ejecutar en modo visible (mostrar navegador)"
    )

    args = parser.parse_args()

    scraper = NewsScraper(headless=not args.headed)
    articles = await scraper.run(
        keyword=args.keyword,
        max_articles=args.max,
        output_format=args.format,
    )

    print(f"\n{'='*50}")
    print(f"Extracción completada: {len(articles)} artículos")
    for article in articles:
        print(f"  - {article.get('title', 'Sin título')}")


if __name__ == "__main__":
    asyncio.run(main())
