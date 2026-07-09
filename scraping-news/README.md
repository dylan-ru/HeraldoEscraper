# El Heraldo News Scraper

Scraper de noticias basado en Python usando Playwright para extraer artículos de [El Heraldo](https://www.elheraldo.hn/).

## Caracteristicas

- Busqueda de noticias por palabra clave
- Extraccion de datos del articulo:
  - Autor
  - Fecha de publicacion (formato ISO 8601)
  - Titulo
  - Descripcion/Lead
  - URL de la imagen principal
  - URL del articulo
- Guardado en CSV o base de datos SQLite
- Manejo anti-paywall
- User-Agent personalizado
- Limitacion de velocidad y delays

## Estructura del Proyecto

```
scraping-news/
├── src/
│   ├── __init__.py      # Inicializacion del paquete
│   ├── config.py        Configuracion
│   ├── scraper.py       # Logica principal del scraper
│   ├── search.py        # Funcionalidad de busqueda
│   ├── extractors.py    # Funciones de extraccion de datos
│   ├── anti_paywall.py  # Eliminacion de paywall
│   ├── storage.py       # Almacenamiento CSV/SQLite
│   └── main.py          # Punto de entrada
├── output/              # Directorio de salida
├── requirements.txt     # Dependencias
├── robots.txt           # Referencia robots.txt
└── README.md            # Este archivo
```

## Instalacion

### Requisitos

- Python 3.8 o superior
- pip

### Setup

1. Clona o descarga este repositorio

2. Crea un entorno virtual (recomendado):
```bash
cd scraping-news
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Instala los navegadores de Playwright:
```bash
playwright install chromium
```

## Uso

### Uso basico

Buscar noticias por palabra clave:

```bash
python -m src.main "tecnologia"
```

### Opciones de CLI

```bash
python -m src.main PALABRA_CLAVE [OPCIONES]

Argumentos:
  PALABRA_CLAVE         Palabra clave de busqueda (requerido)

Opciones:
  -m, --max MAX         Numero maximo de articulos a extraer (Sin esto traera TODOS los resultados)
  -f, --format FORMAT   Formato de salida: csv o sqlite (default: csv)
  --headed              Ejecutar en modo visible (mostrar navegador)
```

### Ejemplos

```bash
# Buscar articulos sobre "economia", max 10 resultados, guardar en CSV
python -m src.main "economia" -m 10 -f csv

# Buscar articulos y guardar en SQLite
python -m src.main "politica" -f sqlite

# Ejecutar con navegador visible para depuracion
python -m src.main "deportes" --headed
```

### Uso programatico

```python
import asyncio
from src.scraper import NewsScraper

async def main():
    scraper = NewsScraper(headless=True)

    articles = await scraper.run(
        keyword="tecnologia",
        max_articles=5,
        output_format="csv"
    )

    for article in articles:
        print(f"Titulo: {article['title']}")
        print(f"URL: {article['article_url']}")
        print(f"Fecha: {article['date']}")
        print("---")

asyncio.run(main())
```

## Salida

### Formato CSV

Los articulos se guardan en `output/articles_YYYYMMDD_HHMMSS.csv` con las columnas:
- title
- author
- date (formato ISO 8601)
- description
- image_url
- article_url

### Formato SQLite

Los articulos se guardan en `output/articles_YYYYMMDD.db` con el esquema:
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    date TEXT,
    description TEXT,
    image_url TEXT,
    article_url TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Configuracion

Edita `src/config.py` para personalizar:

- `USER_AGENT` - Cadena de user-agent del navegador
- `MIN_DELAY` / `MAX_DELAY` - Rango de delay entre solicitudes (segundos)
- `BASE_URL` - URL del sitio objetivo
- `SELECTORS` - Selectores CSS para los elementos
- `PAYWALL_ELEMENTS` - Elementos a eliminar para anti-paywall

## Anti-Paywall

El scraper incluye funcionalidad anti-paywall que:
1. Elimina elementos de paywall (`#ad_position_box`, `#engagement-top`, etiquetas `ins`)
2. Restaura la funcionalidad de scroll
3. Usa MutationObserver para detectar y eliminar paywalls inyectados dinamicamente

## Buenas practicas

1. **Respetar robots.txt**: Revisa el robots.txt del sitio antes de hacer scraping
2. **Limitacion de velocidad**: El scraper agrega delays aleatorios entre solicitudes (1.5-3 segundos)
3. **User-Agent personalizado**: Identifica el scraper como un navegador
4. **Manejo de errores**: Manejo graceful de elementos faltantes y errores

## Soporte Docker (Opcional)

```bash
# Construir la imagen
docker build -t news-scraper .

# Ejecutar el scraper
docker run --rm news-scraper "tecnologia"
```

## Notas

- El scraper esta disenado para El Heraldo (Honduras). Los selectores pueden necesitar ajustes para otros sitios.
- Las fechas de publicacion se parsean del formato espanol a ISO 8601.
- El scraper respeta los limites de velocidad para evitar ser bloqueado.

## Licencia

MIT License
