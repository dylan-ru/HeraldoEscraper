USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

BASE_URL = "https://www.elheraldo.hn"

MIN_DELAY = 1.5
MAX_DELAY = 3.0
PAGE_LOAD_TIMEOUT = 30000
SEARCH_WAIT_TIMEOUT = 6000

OUTPUT_DIR = "output"
DEFAULT_OUTPUT_FORMAT = "csv"

SELECTORS = {
    "author": ".author-name a",
    "date": ".date li.date",
    "title": ".headline",
    "title_alt": ".card-title a h2",
    "description": ".lead",
    "main_image": ".multimedia img",
    "article_url": ".card-title a",

    "menu_toggle": ".m-menu__toggle",
    "search_input": 'input[name="keywords"]',
    "search_button": 'input[aria-label="boton-buscar"]',
    "search_button_alt": "input.iter-button-input-submit",

    "paywall_ad_box": "#ad_position_box",
    "paywall_engagement": "#engagement-top",
    "paywall_ins": "ins",
}

PAYWALL_ELEMENTS = [
    "ad_position_box",
    "engagement-top",
]
