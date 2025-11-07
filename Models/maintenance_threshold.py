# models/maintenance_threshold.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, execute

class MaintenanceThreshold(Base):
    __tablename__ = 'maintenance_threshold'

    thresholdId = Column(Integer, primary_key=True, autoincrement=True)
    locationId = Column(Integer, ForeignKey('store_location.locationId'), nullable=False, unique=True)
    minTemperature = Column(Numeric(5,2), nullable=False)
    maxTemperature = Column(Numeric(5,2), nullable=False)
    minHumidity = Column(Numeric(5,2), nullable=False)
    maxHumidity = Column(Numeric(5,2), nullable=False)

    # Relationships
    location = relationship("StoreLocation", back_populates="threshold")

    def __repr__(self):
        return f"<MaintenanceThreshold(location_id={self.locationId}, temp={self.minTemperature}-{self.maxTemperature}°C)>"

    @staticmethod
    def create(location_id, min_temp, max_temp, min_humidity, max_humidity):
        query = """
            INSERT INTO maintenance_threshold 
            (locationId, minTemperature, maxTemperature, minHumidity, maxHumidity)
            VALUES (?, ?, ?, ?, ?)
        """
        result = execute(query, (location_id, min_temp, max_temp, min_humidity, max_humidity))
        if result is True:
            return True, "Threshold created successfully."
        else:
            raise Exception('Error creating threshold')