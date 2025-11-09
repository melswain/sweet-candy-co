# models/maintenance_alert.py
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base, execute
from datetime import datetime
import enum

class ParameterType(enum.Enum):
    temperature = 'temperature'
    humidity = 'humidity'

class ThresholdBreach(enum.Enum):
    LOW = 'LOW'
    HIGH = 'HIGH'

class MaintenanceAlert(Base):
    __tablename__ = 'maintenance_alert'

    alertId = Column(Integer, primary_key=True, autoincrement=True)
    locationId = Column(Integer, ForeignKey('store_location.locationId'), nullable=False)
    parameterType = Column(Enum(ParameterType))
    value = Column(Numeric(5,2), nullable=False)
    thresholdBreach = Column(Enum(ThresholdBreach))
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    location = relationship("StoreLocation", back_populates="alerts")

    def __repr__(self):
        return f"<MaintenanceAlert(id={self.alertId}, type={self.parameterType}, value={self.value})>"

    @staticmethod
    def create(location_id, parameter_type, value, threshold_breach):
        query = """
            INSERT INTO maintenance_alert (locationId, parameterType, value, thresholdBreach)
            VALUES (?, ?, ?, ?)
        """
        result = execute(query, (location_id, parameter_type, value, threshold_breach))
        if result is True:
            return True, "Alert created successfully."
        else:
            raise Exception('Error creating alert')