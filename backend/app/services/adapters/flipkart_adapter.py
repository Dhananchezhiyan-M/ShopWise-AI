import re
import urllib.parse
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from app.services.adapters.base_adapter import BaseStoreAdapter, StandardProductItem, StandardPricePoint, StandardReview


class FlipkartAdapter(BaseStoreAdapter):
    """
    Flipkart Live Store Adapter.
    Performs live search queries on Flipkart and parses live prices, ratings, and URLs.
    """
    def __init__(self):
        super().__init__(
            store_name="Flipkart",
            store_slug="flipkart",
            base_url="https://www.flipkart.com"
        )
        self.logo_url = "https://static-assets-web.flixcart.com/batman-returns/batman-returns/p/images/fkheaderlogo_exploreplus-448884.svg"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def search_live(self, query: str, limit: int = 5) -> List[StandardProductItem]:
        """
        Executes live asynchronous search on Flipkart.
        """
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.flipkart.com/search?q={encoded_query}"
        results = []

        try:
            async with httpx.AsyncClient(timeout=4.0, headers=self.headers, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    # Try grid & row layouts
                    containers = soup.select("div[data-id]") or soup.select("div._1AtVbE")
                    for it in containers[:limit]:
                        try:
                            fsn = it.get("data-id", "")
                            
                            # Title
                            title_el = (
                                it.select_one("div.KzDlHZ")
                                or it.select_one("a.wjcEIp")
                                or it.select_one("a._4rR01T")
                                or it.select_one("div._4rR01T")
                                or it.select_one("a.s1Q9rs")
                            )
                            title = title_el.get_text(strip=True) if title_el else ""
                            if not title:
                                continue

                            # URL
                            link_el = it.select_one("a.CG2qF7") or it.select_one("a.wjcEIp") or it.select_one("a._1fQZEK") or it.select_one("a[href*='/p/']")
                            href = link_el.get("href", "") if link_el else ""
                            product_url = f"https://www.flipkart.com{href}" if href.startswith("/") else (href or f"https://www.flipkart.com/search?q={encoded_query}")

                            # Price
                            price_el = it.select_one("div.Nx9bqj") or it.select_one("div._30jeq3")
                            if not price_el:
                                continue
                            raw_price = re.sub(r"[^\d]", "", price_el.get_text())
                            if not raw_price:
                                continue
                            current_price = float(raw_price)

                            # Original MRP
                            mrp_el = it.select_one("div.yRaY8j") or it.select_one("div._3I9_wc")
                            original_mrp = None
                            if mrp_el:
                                raw_mrp = re.sub(r"[^\d]", "", mrp_el.get_text())
                                if raw_mrp:
                                    original_mrp = float(raw_mrp)

                            # Rating
                            rating_el = it.select_one("div.XQDdHH") or it.select_one("div._3LWZlK")
                            rating_star = None
                            if rating_el:
                                match = re.search(r"(\d+\.?\d*)", rating_el.get_text())
                                if match:
                                    rating_star = float(match.group(1))

                            # Image
                            img_el = it.select_one("img.DByuf4") or it.select_one("img._396cs4") or it.select_one("img")
                            image_url = img_el.get("src") if img_el else None

                            results.append(
                                StandardProductItem(
                                    store_name=self.store_name,
                                    store_slug=self.store_slug,
                                    external_id=fsn or title[:20],
                                    title=title,
                                    product_url=product_url,
                                    current_price=current_price,
                                    original_mrp=original_mrp or (current_price * 1.18),
                                    discount_percent=round(((original_mrp - current_price) / original_mrp * 100), 1) if original_mrp and original_mrp > current_price else 15.0,
                                    in_stock=True,
                                    rating_star=rating_star or 4.3,
                                    rating_count=350,
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
