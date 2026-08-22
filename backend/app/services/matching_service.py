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
    def calculate_similarity(cls, title_a: str, title_b: str) -> float:
        """Computes Jaccard word-token overlap between two product titles."""
        norm_a = cls.normalize_title(title_a)
        norm_b = cls.normalize_title(title_b)
        
        tokens_a = set(norm_a.split())
        tokens_b = set(norm_b.split())
        
        if not tokens_a or not tokens_b:
            return 0.0
            
        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)
        return len(intersection) / len(union)

    @classmethod
    def extract_specs_from_title(cls, title: str) -> Dict[str, Any]:
        """
        Extracts universal structured specification and dimension tokens from ANY product title
        (Steel bars, Cycles, Scales, Pipes, Tools, Laptops, Audio, Smartphones).
        """
        specs: Dict[str, Any] = {
            "ram_gb": None,
            "storage_gb": None,
            "cpu": None,
            "screen_size": None,
            "dimensions_and_units": [],  # Universal unit tokens (e.g. ['12mm', '12m', '27.5t', '21 speed', '5kg', '1g', '1 inch', '3 meter', 'sdr 11', 'fe 550d'])
            "weight_capacity": None,
            "pack_or_speed": None,
        }

        # 1. Universal Dimensions, Thickness & Diameters (e.g. 12mm, 1 inch, 3 meter, 27.5T)
        dim_matches = re.findall(r"\b(\d+(?:\.\d+)?)\s*(mm|cm|meter|meters|m|inch|inches|\"|t)\b", title, re.IGNORECASE)
        for val, unit in dim_matches:
            unit_clean = "inch" if unit in ['"', "inches"] else ("m" if unit == "meters" else unit.lower())
            specs["dimensions_and_units"].append(f"{val}{unit_clean}")

        # 2. Universal Weights & Capacities (e.g. 5kg, 10kg, 500g, 1g, 10.65kg)
        wt_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(kg|g|gm|grams|ton|mah)\b", title, re.IGNORECASE)
        if wt_match:
            specs["weight_capacity"] = f"{wt_match.group(1)}{wt_match.group(2).lower()}"
            specs["dimensions_and_units"].append(specs["weight_capacity"])

        # 3. Counts, Speeds, Pack Sizes & Grades (e.g. 21 speed, 21s, pack of 10, set of 4, fe 550d, sdr 11)
        speed_match = re.search(r"\b(\d+)\s*(?:speed|s|gear|gears)\b", title, re.IGNORECASE)
        if speed_match:
            specs["pack_or_speed"] = f"{speed_match.group(1)} speed"
            specs["dimensions_and_units"].append(f"{speed_match.group(1)}s")

        pack_match = re.search(r"\b(?:pack|set)\s*of\s*(\d+)\b|\b(\d+)\s*(?:pcs|pieces|units)\b", title, re.IGNORECASE)
        if pack_match:
            count = pack_match.group(1) or pack_match.group(2)
            specs["dimensions_and_units"].append(f"pack of {count}")

        grade_match = re.search(r"\b(fe[-\s]?550d|sdr[-\s]?11|sch[-\s]?40|ip\d{2})\b", title, re.IGNORECASE)
        if grade_match:
            specs["dimensions_and_units"].append(grade_match.group(1).lower().replace(" ", "-"))

        # 4. Electronics: RAM (e.g., 8GB, 16GB, 32GB)
        ram_match = re.search(r"\b(4|8|12|16|24|32|64)\s*gb\s*(?:ram|unified|ddr\d?)?\b", title, re.IGNORECASE)
        if ram_match:
            specs["ram_gb"] = int(ram_match.group(1))
            specs["dimensions_and_units"].append(f"{specs['ram_gb']}gb")

        # 5. Electronics: Storage (e.g., 128GB, 256GB, 512GB, 1TB)
        tb_match = re.search(r"\b(1|2)\s*tb\s*(?:ssd|hdd|nvme|storage)?\b", title, re.IGNORECASE)
        if tb_match:
            specs["storage_gb"] = int(tb_match.group(1)) * 1024
            specs["dimensions_and_units"].append(f"{tb_match.group(1)}tb")
        else:
            storage_match = re.search(r"\b(64|128|256|512)\s*gb\s*(?:ssd|rom|storage|nvme|emmc)?\b", title, re.IGNORECASE)
            if storage_match:
                specs["storage_gb"] = int(storage_match.group(1))

        # 6. Electronics: CPU Processor Family
        if re.search(r"\bi[3579]-?\d{4,5}[a-z]?\b|\bcore\s*i[3579]\b", title, re.IGNORECASE):
            cpu_m = re.search(r"(i[3579]-?\d{4,5}[a-z]?|core\s*i[3579])", title, re.IGNORECASE)
            specs["cpu"] = cpu_m.group(1).upper() if cpu_m else "Intel Core"
        elif re.search(r"\bryzen\s*[3579]\b|\b\d{4}[a-z]?\b", title, re.IGNORECASE):
            specs["cpu"] = "AMD Ryzen"
        elif re.search(r"\bm[1234]\s*(?:pro|max|chip)?\b", title, re.IGNORECASE):
            specs["cpu"] = "Apple Silicon"
        elif re.search(r"\bsnapdragon\b", title, re.IGNORECASE):
            specs["cpu"] = "Snapdragon"

        # 7. Screen Size
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
        and an existing ProductVariant database record for ANY product category.
        """
        norm_title = cls.normalize_title(raw_listing_title)
        extracted = cls.extract_specs_from_title(raw_listing_title)

        score = 0.0

        # 1. Brand Match (Mandatory baseline across all categories)
        if canonical.brand.lower() in norm_title:
            score += 0.35
        else:
            return 0.0  # Different brand -> 0% match (e.g. Hero != Firefox, Tata != Jindal)

        # 2. Model Family Match (e.g. Target 21S, Slim 3, Chef-Mate, CPVC Pro, Tiscon 550D)
        if canonical.base_model:
            bm_lower = canonical.base_model.lower()
            if bm_lower in norm_title:
                score += 0.35
            else:
                # Check partial model token overlap (e.g. 'Slim 3' in 'IdeaPad Slim 3')
                bm_tokens = set(bm_lower.split())
                title_tokens = set(norm_title.split())
                overlap = bm_tokens.intersection(title_tokens)
                if overlap:
                    score += 0.35 * (len(overlap) / len(bm_tokens))
                else:
                    jaccard = cls.calculate_similarity(raw_listing_title, canonical.title)
                    score += jaccard * 0.25

        # 3. Universal Dimension & Spec Token Check
        # Compare extracted tokens against variant_name and specifications_json
        variant_desc = (variant.variant_name or "").lower()
        if variant.specifications_json:
            variant_desc += " " + variant.specifications_json.lower()

        variant_tokens = cls.extract_specs_from_title(variant_desc)["dimensions_and_units"]
        listing_tokens = extracted["dimensions_and_units"]

        if listing_tokens and variant_tokens:
            overlap = set(listing_tokens).intersection(set(variant_tokens))
            if overlap:
                score += 0.20
            else:
                # If both specify distinct conflicting units (e.g. 16mm vs 12mm, 29T vs 27.5T, 8GB vs 16GB), reject!
                for l_tok in listing_tokens:
                    # Check if conflicting dimension of same type exists
                    val_num = re.findall(r"\d+", l_tok)
                    if val_num:
                        for v_tok in variant_tokens:
                            if any(unit in l_tok and unit in v_tok for unit in ["mm", "inch", "gb", "kg", "speed", "s", "t"]) and l_tok != v_tok:
                                return 0.0  # Conflict! Not the same variant (e.g. 12mm vs 16mm rod)

        # 4. Electronics RAM / Storage Check
        if extracted.get("ram_gb") is not None and variant.ram_gb is not None:
            if extracted["ram_gb"] == variant.ram_gb:
                score += 0.10
            else:
                return 0.0

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

        import json

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

                # Parse specifications_json if present
                extra_specs = {}
                if variant.specifications_json:
                    try:
                        extra_specs = json.loads(variant.specifications_json)
                    except Exception:
                        extra_specs = {"raw_specs": variant.specifications_json}

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
                        **extra_specs,  # Merges thickness, length, wheel size, capacity, etc.
                    },
                    "specifications_json": extra_specs,
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
