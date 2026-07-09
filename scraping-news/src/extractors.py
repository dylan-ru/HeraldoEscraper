import re
from datetime import datetime
from typing import Optional, Dict, List
from dateutil import parser as date_parser

from src.config import SELECTORS, BASE_URL


SPANISH_MONTHS = {
    "enero": "January",
    "febrero": "February",
    "marzo": "March",
    "abril": "April",
    "mayo": "May",
    "junio": "June",
    "julio": "July",
    "agosto": "August",
    "septiembre": "September",
    "octubre": "October",
    "noviembre": "November",
    "diciembre": "December",
}


def parse_spanish_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None

    date_str = date_str.strip()
    date_str = re.sub(r'^(Actualizado|Publicado):\s*', '', date_str, flags=re.IGNORECASE)

    for spanish, english in SPANISH_MONTHS.items():
        date_str = date_str.replace(spanish, english)

    date_str = date_str.replace(" a las ", " ")
    date_str = date_str.replace(" de ", " ")

    try:
        parsed_date = date_parser.parse(date_str, fuzzy=True)
        return parsed_date.isoformat()
    except (ValueError, TypeError) as e:
        print(f"[WARN] No se pudo parsear la fecha '{date_str}': {e}")
        return None


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_author(element) -> Optional[str]:
    try:
        author_text = element.text_content() or ""
        author_text = clean_text(author_text)
        author_text = re.sub(r'\s*seguir\s*\+?\s*$', '', author_text)
        return author_text if author_text else None
    except Exception:
        return None


def extract_date(element) -> Optional[str]:
    try:
        date_text = element.text_content() or ""
        return parse_spanish_date(date_text)
    except Exception:
        return None


def extract_title(element) -> Optional[str]:
    try:
        title_text = element.text_content() or ""
        return clean_text(title_text) if title_text else None
    except Exception:
        return None


def extract_description(element) -> Optional[str]:
    try:
        desc_text = element.text_content() or ""
        return clean_text(desc_text) if desc_text else None
    except Exception:
        return None


def extract_image_url(element) -> Optional[str]:
    try:
        src = element.get_attribute("src")
        if src and not src.startswith("data:"):
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = BASE_URL + src
            return src
        return None
    except Exception:
        return None


def extract_article_url(element) -> Optional[str]:
    try:
        href = element.get_attribute("href")
        if href:
            if href.startswith("/"):
                href = BASE_URL + href
            return href
        return None
    except Exception:
        return None


async def extract_article_data(page, article_element) -> Dict:
    data = {
        "author": None,
        "date": None,
        "title": None,
        "description": None,
        "image_url": None,
        "article_url": None,
    }

    try:
        author_el = article_element.locator(SELECTORS["author"])
        if await author_el.count() > 0:
            data["author"] = extract_author(author_el.first)

        date_el = article_element.locator(SELECTORS["date"])
        if await date_el.count() > 0:
            data["date"] = extract_date(date_el.first)

        title_el = article_element.locator(SELECTORS["title"])
        if await title_el.count() > 0:
            data["title"] = extract_title(title_el.first)
        else:
            title_el = article_element.locator(SELECTORS["title_alt"])
            if await title_el.count() > 0:
                data["title"] = extract_title(title_el.first)

        desc_el = article_element.locator(SELECTORS["description"])
        if await desc_el.count() > 0:
            data["description"] = extract_description(desc_el.first)

        img_el = article_element.locator(SELECTORS["main_image"])
        if await img_el.count() > 0:
            data["image_url"] = extract_image_url(img_el.first)

        url_el = article_element.locator(SELECTORS["article_url"])
        if await url_el.count() > 0:
            data["article_url"] = extract_article_url(url_el.first)

    except Exception as e:
        print(f"[ERROR] Error al extraer datos del artículo: {e}")

    return data


async def extract_search_results(page) -> List[Dict]:
    articles = []

    article_cards = page.locator(".card-title.title a")

    count = await article_cards.count()
    print(f"Se encontraron {count} artículos en los resultados de búsqueda")

    for i in range(count):
        card = article_cards.nth(i)

        article_url = await card.get_attribute("href")
        if article_url and article_url.startswith("/"):
            article_url = BASE_URL + article_url

        title = await card.text_content()
        title = clean_text(title) if title else None

        if article_url:
            articles.append({
                "title": title,
                "article_url": article_url,
                "author": None,
                "date": None,
                "description": None,
                "image_url": None,
            })

    return articles


async def extract_full_article(page) -> Dict:
    data = {
        "author": None,
        "date": None,
        "title": None,
        "description": None,
        "image_url": None,
        "article_url": page.url,
    }

    try:
        author_el = page.locator(SELECTORS["author"])
        if await author_el.count() > 0:
            data["author"] = await author_el.first.text_content()
            if data["author"]:
                data["author"] = re.sub(r'\s*seguir\s*\+?\s*$', '', clean_text(data["author"]))

        date_el = page.locator(SELECTORS["date"])
        if await date_el.count() > 0:
            date_text = await date_el.first.text_content()
            if date_text:
                data["date"] = parse_spanish_date(date_text)

        title_el = page.locator(SELECTORS["title"])
        if await title_el.count() > 0:
            title_text = await title_el.first.text_content()
            if title_text:
                data["title"] = clean_text(title_text)

        desc_el = page.locator(SELECTORS["description"])
        if await desc_el.count() > 0:
            desc_text = await desc_el.first.text_content()
            if desc_text:
                data["description"] = clean_text(desc_text)

        img_el = page.locator(SELECTORS["main_image"])
        if await img_el.count() > 0:
            src = await img_el.first.get_attribute("src")
            if src and not src.startswith("data:"):
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = BASE_URL + src
                data["image_url"] = src

    except Exception as e:
        print(f"[ERROR] Error al extraer artículo completo: {e}")

    return data
