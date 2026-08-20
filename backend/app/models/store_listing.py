import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class StoreListing(Base):
    """
    A specific retailer listing page for a product variant.
    (e.g., Lenovo IdeaPad Slim 3 16GB listed on Amazon India for ₹55,999)
    """
    __tablename__ = "store_listings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    
    external_product_id = Column(String(100), nullable=True, index=True)  # ASIN (Amazon), FSN (Flipkart)
    product_url = Column(String(1000), nullable=False)                    # Direct store link
    title_in_store = Column(String(500), nullable=False)                 # Raw title listed in the store
    
    current_price = Column(Float, nullable=False, index=True)            # Current selling price (INR)
    original_mrp = Column(Float, nullable=True)                          # MRP / Maximum Retail Price
    discount_percent = Column(Float, nullable=True)                      # Calculated discount %
    in_stock = Column(Boolean, default=True)                             # Stock availability
    
    # Store-specific user ratings
    rating_star = Column(Float, nullable=True)                           # e.g., 4.4
    rating_count = Column(Integer, nullable=True)                        # e.g., 8210 verified reviews
    
    last_scraped_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    variant = relationship("ProductVariant", back_populates="store_listings")
    store = relationship("Store", back_populates="listings")
    price_history = relationship("PriceHistoryRecord", back_populates="store_listing", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StoreListing(id={self.id}, store_id={self.store_id}, price=₹{self.current_price})>"
