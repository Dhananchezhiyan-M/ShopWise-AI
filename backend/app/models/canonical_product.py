import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class CanonicalProduct(Base):
    """
    Master product entity representing a unified product identity
    across different retailers and variants.
    """
    __tablename__ = "canonical_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # 'laptop', 'smartphone', 'audio', 'smartwatch'
    base_model = Column(String(150), nullable=True)
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    variants = relationship("ProductVariant", back_populates="canonical_product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CanonicalProduct(id={self.id}, title='{self.title}', brand='{self.brand}')>"
