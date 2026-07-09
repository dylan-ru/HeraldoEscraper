import asyncio
from src.config import SELECTORS, SEARCH_WAIT_TIMEOUT, PAGE_LOAD_TIMEOUT


async def search_news(page, keyword: str) -> bool:
    print(f'Buscando: "{keyword}"...')

    menu_toggle = page.locator(SELECTORS["menu_toggle"])

    if await menu_toggle.count() > 0:
        await menu_toggle.first.click()
        print("[OK] Menú abierto. Esperando campo de búsqueda...")
    else:
        print("[ERROR] Botón de menú no encontrado.")
        return False

    search_input = page.locator(SELECTORS["search_input"])

    try:
        await search_input.wait_for(state="visible", timeout=SEARCH_WAIT_TIMEOUT)
        print("[OK] Campo de búsqueda encontrado.")
    except Exception:
        print("[ERROR] Tiempo agotado. Campo de búsqueda no encontrado.")
        return False

    await search_input.focus()
    await search_input.fill("")
    await search_input.fill(keyword)
    await search_input.dispatch_event("change")
    print(f'[OK] Palabra clave "{keyword}" ingresada.')

    await asyncio.sleep(0.8)

    search_button = page.locator(SELECTORS["search_button"])

    if await search_button.count() > 0:
        async with page.expect_navigation(wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT):
            await search_button.click()
        print("[OK] Botón de búsqueda clickeado.")
    else:
        alt_button = page.locator(SELECTORS["search_button_alt"])
        if await alt_button.count() > 0:
            async with page.expect_navigation(wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT):
                await alt_button.click()
            print("[OK] Botón de búsqueda alternativo clickeado.")
        else:
            print("[WARN] Usando tecla Enter como respaldo...")
            await search_input.press("Enter")
            await page.wait_for_load_state("domcontentloaded")

    await asyncio.sleep(1)
    return True
