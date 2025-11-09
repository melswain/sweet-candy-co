# models/environment_reading.py
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute
from datetime import datetime

class EnvironmentReading(Base):
    __tablename__ = 'environment_reading'

    readingId = Column(Integer, primary_key=True, autoincrement=True)
    locationId = Column(Integer, ForeignKey('store_location.locationId'), nullable=False)
    temperature = Column(Numeric(5,2), nullable=False)
    humidity = Column(Numeric(5,2), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    location = relationship("StoreLocation", back_populates="readings")

    def __repr__(self):
        return f"<EnvironmentReading(id={self.readingId}, temp={self.temperature}°C, humidity={self.humidity}%)>"

    @staticmethod
    def create(location_id, temperature, humidity):
        query = """
            INSERT INTO environment_reading (locationId, temperature, humidity)
            VALUES (?, ?, ?)
        """
        result = execute(query, (location_id, temperature, humidity))
        if result is True:
            return True, "Reading recorded successfully."
        else:
            raise Exception('Error recording reading')