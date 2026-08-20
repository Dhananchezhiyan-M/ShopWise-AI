import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PriceHistoryRecord(Base):
    """
    Time-series historical price log for a store listing.
    Enables 30/90-day moving average and all-time low calculations.
    """
    __tablename__ = "price_history_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_listing_id = Column(Integer, ForeignKey("store_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Relationships
    store_listing = relationship("StoreListing", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistoryRecord(listing_id={self.store_listing_id}, price=₹{self.price}, date={self.recorded_at})>"
