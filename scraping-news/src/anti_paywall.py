from src.config import PAYWALL_ELEMENTS, SELECTORS


async def remove_paywall(page) -> bool:
    removed = False

    for element_id in PAYWALL_ELEMENTS:
        removed_count = await page.evaluate(f"""
            () => {{
                const el = document.getElementById('{element_id}');
                if (el) {{
                    el.remove();
                    return 1;
                }}
                return 0;
            }}
        """)
        if removed_count > 0:
            removed = True

    ins_removed = await page.evaluate("""
        () => {
            const insElements = document.querySelectorAll('ins');
            const count = insElements.length;
            insElements.forEach(el => el.remove());
            return count;
        }
    """)
    if ins_removed > 0:
        removed = True

    if removed:
        await page.evaluate("""
            () => {
                document.body.removeAttribute('style');
                document.documentElement.removeAttribute('style');
            }
        """)

    return removed


async def setup_paywall_observer(page):
    await page.evaluate("""
        () => {
            function eliminarPaywall() {
                let eliminado = false;
                const adBox = document.getElementById('ad_position_box');
                if (adBox) { adBox.remove(); eliminado = true; }
                const engagement = document.getElementById('engagement-top');
                if (engagement) { engagement.remove(); eliminado = true; }
                const insElements = document.querySelectorAll('ins');
                if (insElements.length > 0) { insElements.forEach(el => el.remove()); eliminado = true; }
                if (eliminado) { document.body.removeAttribute('style'); document.documentElement.removeAttribute('style'); }
                return eliminado;
            }
            eliminarPaywall();
            const observer = new MutationObserver((mutations) => {
                let encontrado = false;
                for (const mutation of mutations) {
                    for (const node of mutation.addedNodes) {
                        if (node.id === 'ad_position_box' || node.id === 'engagement-top' || node.nodeName === 'INS') { encontrado = true; break; }
                        if (node.querySelector && (node.querySelector('#ad_position_box') || node.querySelector('#engagement-top') || node.querySelector('ins'))) { encontrado = true; break; }
                    }
                    if (encontrado) break;
                }
                if (encontrado) eliminarPaywall();
            });
            observer.observe(document.documentElement, { childList: true, subtree: true });
        }
    """)
