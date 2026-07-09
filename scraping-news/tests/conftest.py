"""
Pytest configuration and fixtures for the news scraper tests.
"""

import pytest
import asyncio
import os
import sys
import tempfile
import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_article():
    """Sample article data for testing."""
    return {
        "title": "Unidos por el agua: Escolares abrazan la naturaleza",
        "author": "Alberto Cerrato",
        "date": "2026-06-25T16:18:00",
        "description": "Junto a la alcaldía capitalina y UMAPS, líderes ecológicos recorren la planta de tratamiento",
        "image_url": "https://www.elheraldo.hn/binrepository/1260x945/test.jpg",
        "article_url": "https://www.elheraldo.hn/tegucigalpa/unidos-por-agua-IC31225085",
    }


@pytest.fixture
def sample_articles_list():
    """List of sample articles for testing."""
    return [
        {
            "title": "Article 1",
            "author": "Author 1",
            "date": "2026-06-25T10:00:00",
            "description": "Description 1",
            "image_url": "https://example.com/img1.jpg",
            "article_url": "https://www.elheraldo.hn/article1",
        },
        {
            "title": "Article 2",
            "author": "Author 2",
            "date": "2026-06-25T11:00:00",
            "description": "Description 2",
            "image_url": "https://example.com/img2.jpg",
            "article_url": "https://www.elheraldo.hn/article2",
        },
        {
            "title": "Article 3",
            "author": "Author 3",
            "date": "2026-06-25T12:00:00",
            "description": "Description 3",
            "image_url": "https://example.com/img3.jpg",
            "article_url": "https://www.elheraldo.hn/article3",
        },
    ]


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_sqlite_db(temp_output_dir):
    """Create a temporary SQLite database for testing."""
    db_path = os.path.join(temp_output_dir, "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            date TEXT,
            description TEXT,
            image_url TEXT,
            article_url TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    yield db_path


@pytest.fixture
def mock_page():
    """Mock Playwright page object."""
    page = AsyncMock()
    page.url = "https://www.elheraldo.hn/test-article"
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.evaluate = MagicMock(return_value=0)
    page.set_default_timeout = MagicMock()
    return page


@pytest.fixture
def mock_browser():
    """Mock Playwright browser object."""
    browser = AsyncMock()
    browser.close = AsyncMock()
    return browser


@pytest.fixture
def mock_context():
    """Mock Playwright context object."""
    context = AsyncMock()
    context.new_page = AsyncMock()
    return context


@pytest.fixture
def sample_html_article():
    """Sample HTML for an article page."""
    return """
    <html>
    <body>
        <div class="author-name">
            <a href="/autores/-/meta/alberto-cerrato">Alberto Cerrato <span class="seguir">seguir +</span></a>
        </div>
        <div class="date">
            <ul>
                <li class="date">Actualizado: 25 de junio de 2026 a las 16:18</li>
            </ul>
        </div>
        <div class="RE24_TIT card border-0">
            <h1 class="headline">Unidos por el agua: Escolares abrazan la naturaleza</h1>
        </div>
        <div class="RE24_LEAD card border-0">
            <h2 class="lead">Junto a la alcaldía capitalina y UMAPS</h2>
        </div>
        <div class="multimedia">
            <img src="https://www.elheraldo.hn/binrepository/test.jpg" />
        </div>
        <div class="card-title title">
            <a href="/article/test-123"><h2>Test Article</h2></a>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_search_results_html():
    """Sample HTML for search results page."""
    return """
    <html>
    <body>
        <div class="card-title title">
            <a href="/article1"><h2>Article 1</h2></a>
        </div>
        <div class="card-title title">
            <a href="/article2"><h2>Article 2</h2></a>
        </div>
        <div class="card-title title">
            <a href="/article3"><h2>Article 3</h2></a>
        </div>
    </body>
    </html>
    """
