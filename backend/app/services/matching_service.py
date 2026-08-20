import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import CanonicalProduct, ProductVariant, StoreListing, Store


class ProductMatchingService:
    """
    Service responsible for normalizing product titles, extracting hardware tokens,
    and resolving differing retailer listings into unified Canonical Products.
    """

    # Common noise terms to strip from product titles
    NOISE_WORDS = [
        r"\bthin and light\b",
        r"\blaptop\b",
        r"\bheadset\b",
        r"\bheadphones\b",
        r"\bearphones\b",
        r"\bsmartphone\b",
        r"\bmobile phone\b",
        r"\bwith mic\b",
        r"\bwith microphone\b",
        r"\bwindows 11 home\b",
        r"\bwin 11\b",
        r"\bms office 2021\b",
        r"\bmso 21\b",
        r"\bms office\b",
        r"\bofficial warranty\b",
        r"\bgenuine\b",
        r"\bbrand new\b",
        r"\bfree delivery\b",
    ]

    @classmethod
    def normalize_title(cls, raw_title: str) -> str:
        """
        Cleans and normalizes raw product title by removing marketing noise,
        standardizing punctuation, and normalizing whitespace.
        """
        if not raw_title:
            return ""

        title = raw_title.lower()

        # Remove noise phrases
        for noise_pattern in cls.NOISE_WORDS:
            title = re.sub(noise_pattern, " ", title, flags=re.IGNORECASE)

        # Standardize symbols (e.g. 15.6" -> 15.6 inch)
        title = re.sub(r'(\d+(\.\d+)?)\s*("|inch|inches)', r"\1 inch ", title)
        
        # Standardize RAM/Storage formats (e.g., 16 gb -> 16gb, 512 gb ssd -> 512gb ssd)
        title = re.sub(r'(\d+)\s*gb\b', r'\1gb', title)
        title = re.sub(r'(\d+)\s*tb\b', r'\1tb', title)

        # Remove special punctuation and extra spaces
        title = re.sub(r"[^\w\s\.\-]", " ", title)
        title = re.sub(r"\s+", " ", title).strip()

        return title

    @classmethod
    def extract_specs_from_title(cls, title: str) -> Dict[str, Any]:
        """
        Extracts key structured specification tokens from a normalized or raw title.
        """
        specs: Dict[str, Any] = {
            "ram_gb": None,
            "storage_gb": None,
            "cpu": None,
            "screen_size": None,
        }

        # 1. Extract RAM (e.g., 8GB, 16GB, 32GB)
        ram_match = re.search(r"\b(4|8|12|16|24|32|64)\s*gb\s*(?:ram|unified|ddr\d?)?\b", title, re.IGNORECASE)
        if ram_match:
            specs["ram_gb"] = int(ram_match.group(1))

        # 2. Extract Storage (e.g., 128GB, 256GB, 512GB, 1TB)
        tb_match = re.search(r"\b(1|2)\s*tb\s*(?:ssd|hdd|nvme|storage)?\b", title, re.IGNORECASE)
        if tb_match:
            specs["storage_gb"] = int(tb_match.group(1)) * 1024
        else:
            storage_match = re.search(r"\b(64|128|256|512)\s*gb\s*(?:ssd|rom|storage|nvme|emmc)?\b", title, re.IGNORECASE)
            if storage_match:
                specs["storage_gb"] = int(storage_match.group(1))

        # 3. Extract CPU Processor Family
        if re.search(r"\bi[3579]-?\d{4,5}[a-z]?\b|\bcore\s*i[3579]\b", title, re.IGNORECASE):
            cpu_m = re.search(r"(i[3579]-?\d{4,5}[a-z]?|core\s*i[3579])", title, re.IGNORECASE)
            specs["cpu"] = cpu_m.group(1).upper() if cpu_m else "Intel Core"
        elif re.search(r"\bryzen\s*[3579]\b|\b\d{4}[a-z]?\b", title, re.IGNORECASE):
            specs["cpu"] = "AMD Ryzen"
        elif re.search(r"\bm[1234]\s*(?:pro|max|chip)?\b", title, re.IGNORECASE):
            specs["cpu"] = "Apple Silicon"
        elif re.search(r"\bsnapdragon\b", title, re.IGNORECASE):
            specs["cpu"] = "Snapdragon"

        # 4. Extract Screen Size
        screen_m = re.search(r"\b(13\.\d|14(\.\d)?|15\.\d|16(\.\d)?|17\.\d)\s*(?:inch|\")?\b", title, re.IGNORECASE)
        if screen_m:
            specs["screen_size"] = float(screen_m.group(1))

        return specs

    @classmethod
    def calculate_match_score(
        cls,
        raw_listing_title: str,
        variant: ProductVariant,
        canonical: CanonicalProduct
    ) -> float:
        """
        Calculates similarity score (0.0 to 1.0) between a raw store listing title
        and an existing ProductVariant database record.
        """
        norm_title = cls.normalize_title(raw_listing_title)
        extracted = cls.extract_specs_from_title(raw_listing_title)

        score = 0.0

        # Check Brand Match (Mandatory)
        if canonical.brand.lower() in norm_title:
            score += 0.35
        else:
            return 0.0  # Different brand -> 0% match

        # Check Model Family Match
        if canonical.base_model and canonical.base_model.lower() in norm_title:
            score += 0.35

        # Check RAM match (Strict: If listing specifies RAM, it MUST match the variant RAM)
        if extracted.get("ram_gb") is not None and variant.ram_gb is not None:
            if extracted["ram_gb"] == variant.ram_gb:
                score += 0.15
            else:
                return 0.0  # Different RAM variant -> Not the same product!

        # Check Storage match
        if extracted.get("storage_gb") is not None and variant.storage_gb is not None:
            if extracted["storage_gb"] == variant.storage_gb:
                score += 0.15
            else:
                score -= 0.10

        return min(1.0, score)

    @classmethod
    def get_canonical_catalog(
        cls,
        db: Session,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        max_budget: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves canonical products with all resolved multi-store listings,
        calculating lowest price, price differences, and store badges.
        """
        query = db.query(CanonicalProduct)

        if category and category.lower() != "all":
            query = query.filter(CanonicalProduct.category == category.lower())

        if search_query:
            query = query.filter(
                or_(
                    CanonicalProduct.title.ilike(f"%{search_query}%"),
                    CanonicalProduct.brand.ilike(f"%{search_query}%"),
                    CanonicalProduct.base_model.ilike(f"%{search_query}%"),
                    CanonicalProduct.description.ilike(f"%{search_query}%"),
                )
            )

        canonicals = query.all()
        results = []

        for prod in canonicals:
            for variant in prod.variants:
                listings = variant.store_listings
                if not listings:
                    continue

                # Filter by max budget if provided
                prices = [l.current_price for l in listings]
                min_price = min(prices)
                max_price = max(prices)

                if max_budget and min_price > max_budget:
                    continue

                # Sort listings so cheapest store is first
                sorted_listings = sorted(listings, key=lambda l: l.current_price)
                best_listing = sorted_listings[0]

                # Format multi-store comparison cards
                stores_comparison = []
                for l in sorted_listings:
                    savings = l.current_price - min_price
                    stores_comparison.append({
                        "listing_id": l.id,
                        "store_name": l.store.name,
                        "store_slug": l.store.slug,
                        "store_logo": l.store.logo_url,
                        "title_in_store": l.title_in_store,
                        "product_url": l.product_url,
                        "current_price": l.current_price,
                        "original_mrp": l.original_mrp,
                        "discount_percent": l.discount_percent,
                        "rating_star": l.rating_star,
                        "rating_count": l.rating_count,
                        "is_cheapest": l.id == best_listing.id,
                        "price_difference_vs_lowest": round(savings, 2),
                    })

                results.append({
                    "canonical_id": prod.id,
                    "variant_id": variant.id,
                    "title": prod.title,
                    "brand": prod.brand,
                    "category": prod.category,
                    "base_model": prod.base_model,
                    "image_url": prod.image_url,
                    "description": prod.description,
                    "variant_name": variant.variant_name,
                    "specs": {
                        "ram_gb": variant.ram_gb,
                        "storage_gb": variant.storage_gb,
                        "cpu": variant.cpu_processor,
                        "gpu": variant.gpu_graphics,
                        "screen_size": variant.screen_size_inch,
                        "battery": variant.battery_specs,
                        "color": variant.color,
                    },
                    "pricing": {
                        "lowest_price": min_price,
                        "highest_price": max_price,
                        "best_store_name": best_listing.store.name,
                        "best_store_slug": best_listing.store.slug,
                        "best_store_url": best_listing.product_url,
                        "store_count": len(stores_comparison),
                    },
                    "store_listings": stores_comparison,
                })

        # Sort overall results by lowest price ascending
        results.sort(key=lambda r: r["pricing"]["lowest_price"])
        return results
