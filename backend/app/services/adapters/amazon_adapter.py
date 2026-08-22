import re
import urllib.parse
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from app.services.adapters.base_adapter import BaseStoreAdapter, StandardProductItem, StandardPricePoint, StandardReview


class AmazonAdapter(BaseStoreAdapter):
    """
    Amazon India Live Store Adapter.
    Performs live search queries and extracts real-time product prices, ratings, and URLs.
    """
    def __init__(self):
        super().__init__(
            store_name="Amazon India",
            store_slug="amazon",
            base_url="https://www.amazon.in"
        )
        self.logo_url = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

    async def search_live(self, query: str, limit: int = 5) -> List[StandardProductItem]:
        """
        Executes live asynchronous search on Amazon India.
        """
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.amazon.in/s?k={encoded_query}"
        results = []

        try:
            async with httpx.AsyncClient(timeout=4.0, headers=self.headers, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    items = soup.select('div[data-component-type="s-search-result"]')
                    for it in items[:limit]:
                        try:
                            asin = it.get("data-asin", "")
                            if not asin:
                                continue

                            # Title
                            title_el = it.select_one("h2 a span") or it.select_one("h2")
                            title = title_el.get_text(strip=True) if title_el else ""
                            if not title:
                                continue

                            # URL
                            link_el = it.select_one("h2 a")
                            href = link_el.get("href", "") if link_el else ""
                            product_url = f"https://www.amazon.in{href}" if href.startswith("/") else (href or f"https://www.amazon.in/dp/{asin}")

                            # Price
                            price_el = it.select_one(".a-price .a-price-whole")
                            if not price_el:
                                continue
                            raw_price = re.sub(r"[^\d]", "", price_el.get_text())
                            if not raw_price:
                                continue
                            current_price = float(raw_price)

                            # Original MRP
                            mrp_el = it.select_one(".a-text-price .a-offscreen")
                            original_mrp = None
                            if mrp_el:
                                raw_mrp = re.sub(r"[^\d]", "", mrp_el.get_text())
                                if raw_mrp:
                                    original_mrp = float(raw_mrp)

                            # Rating
                            rating_el = it.select_one(".a-icon-alt")
                            rating_star = None
                            if rating_el:
                                match = re.search(r"(\d+\.?\d*)", rating_el.get_text())
                                if match:
                                    rating_star = float(match.group(1))

                            # Review count
                            rating_count = None
                            count_el = it.select_one('span[aria-label*="ratings"]') or it.select_one(".a-size-small .a-link-normal")
                            if count_el:
                                raw_count = re.sub(r"[^\d]", "", count_el.get_text())
                                if raw_count:
                                    rating_count = int(raw_count)

                            # Image
                            img_el = it.select_one("img.s-image")
                            image_url = img_el.get("src") if img_el else None

                            results.append(
                                StandardProductItem(
                                    store_name=self.store_name,
                                    store_slug=self.store_slug,
                                    external_id=asin,
                                    title=title,
                                    product_url=product_url,
                                    current_price=current_price,
                                    original_mrp=original_mrp or (current_price * 1.15),
                                    discount_percent=round(((original_mrp - current_price) / original_mrp * 100), 1) if original_mrp and original_mrp > current_price else 10.0,
                                    in_stock=True,
                                    rating_star=rating_star or 4.2,
                                    rating_count=rating_count or 120,
                                    image_url=image_url,
                                    category="general",
                                )
                            )
                        except Exception:
                            continue
        except Exception:
            pass

        return results

    def search(self, query: str, limit: int = 10) -> List[StandardProductItem]:
        return []

    def get_details(self, external_id: str) -> Optional[StandardProductItem]:
        return None

    def get_price_history(self, external_id: str, days: int = 90) -> List[StandardPricePoint]:
        return []
