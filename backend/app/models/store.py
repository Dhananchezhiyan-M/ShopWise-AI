import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Store(Base):
    """
    E-commerce retailer platform (e.g., Amazon, Flipkart, Croma).
    """
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)  # 'Amazon', 'Flipkart', 'Croma'
    slug = Column(String(50), nullable=False, unique=True, index=True)  # 'amazon', 'flipkart', 'croma'
    logo_url = Column(String(500), nullable=True)
    base_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    listings = relationship("StoreListing", back_populates="store", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Store(id={self.id}, name='{self.name}', slug='{self.slug}')>"
