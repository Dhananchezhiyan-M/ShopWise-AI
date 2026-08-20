import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProductVariant(Base):
    """
    Specific hardware/spec configuration of a canonical product
    (e.g., 16GB RAM, 512GB SSD, Intel i5, Arctic Grey).
    """
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    canonical_product_id = Column(Integer, ForeignKey("canonical_products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    variant_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True, unique=True, index=True)
    
    # Core hardware specifications for structured filtering
    ram_gb = Column(Integer, nullable=True, index=True)          # e.g., 8, 16, 32
    storage_gb = Column(Integer, nullable=True, index=True)      # e.g., 256, 512, 1024
    cpu_processor = Column(String(150), nullable=True)          # e.g., 'Intel Core i5-12450H', 'Apple M3'
    gpu_graphics = Column(String(150), nullable=True)           # e.g., 'Intel Iris Xe', 'RTX 4050'
    screen_size_inch = Column(Float, nullable=True)             # e.g., 15.6, 14.0
    battery_specs = Column(String(150), nullable=True)          # e.g., '45Wh (Up to 7 hours)'
    color = Column(String(50), nullable=True)                   # e.g., 'Arctic Grey', 'Midnight'
    
    # JSON-encoded string for flexible category-specific extra specs
    specifications_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    canonical_product = relationship("CanonicalProduct", back_populates="variants")
    store_listings = relationship("StoreListing", back_populates="variant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductVariant(id={self.id}, name='{self.variant_name}', RAM={self.ram_gb}GB, Storage={self.storage_gb}GB)>"
