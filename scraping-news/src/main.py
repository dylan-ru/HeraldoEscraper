import asyncio
import sys
from src.scraper import NewsScraper, main


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExtracción interrumpida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
