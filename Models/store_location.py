# models/store_location.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base, execute

class StoreLocation(Base):
    __tablename__ = 'store_location'

    locationId = Column(Integer, primary_key=True, autoincrement=True)
    locationName = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)

    # Relationships
    inventory = relationship("Inventory", back_populates="location")
    readings = relationship("EnvironmentReading", back_populates="location")
    alerts = relationship("MaintenanceAlert", back_populates="location")
    threshold = relationship("MaintenanceThreshold", back_populates="location", uselist=False)

    def __repr__(self):
        return f"<StoreLocation(name='{self.locationName}', address='{self.address}')>"

    @staticmethod
    def create(name, address):
        query = """
            INSERT INTO store_location (locationName, address)
            VALUES (?, ?)
        """
        result = execute(query, (name, address))
        if result is True:
            return True, "Store location created successfully."
        else:
            raise Exception('Error creating store location')