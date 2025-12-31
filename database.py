"""
Database Models for Smart Agriculture Platform
Handles sensor data and recommendation storage
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class SensorData(Base):
    """Store historical sensor readings"""

    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    soil_moisture = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    location = Column(String(100), default="Field-1")

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "soil_moisture": self.soil_moisture,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "location": self.location,
        }


class Recommendation(Base):
    """Store irrigation and fertilizer recommendations with reasoning"""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    sensor_data_id = Column(Integer, nullable=False)

    # Irrigation recommendation
    irrigation_action = Column(
        String(50), nullable=False
    )  # "water", "no_action", "reduce"
    irrigation_amount = Column(Float, nullable=True)  # liters per m²
    irrigation_reasoning = Column(Text, nullable=False)

    # Fertilizer recommendation
    fertilizer_action = Column(String(50), nullable=False)  # "apply", "no_action"
    fertilizer_type = Column(String(100), nullable=True)
    fertilizer_reasoning = Column(Text, nullable=False)

    # Alerts
    alert_level = Column(String(20), nullable=False)  # "none", "warning", "critical"
    alert_message = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "sensor_data_id": self.sensor_data_id,
            "irrigation_action": self.irrigation_action,
            "irrigation_amount": self.irrigation_amount,
            "irrigation_reasoning": self.irrigation_reasoning,
            "fertilizer_action": self.fertilizer_action,
            "fertilizer_type": self.fertilizer_type,
            "fertilizer_reasoning": self.fertilizer_reasoning,
            "alert_level": self.alert_level,
            "alert_message": self.alert_message,
        }


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_url="sqlite:///smart_agriculture.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()

    def add_sensor_data(self, soil_moisture, temperature, humidity, location="Field-1"):
        """Add new sensor reading"""
        session = self.get_session()
        try:
            sensor_data = SensorData(
                soil_moisture=soil_moisture,
                temperature=temperature,
                humidity=humidity,
                location=location,
            )
            session.add(sensor_data)
            session.commit()
            session.refresh(sensor_data)
            return sensor_data
        finally:
            session.close()

    def add_recommendation(self, recommendation_data):
        """Add new recommendation"""
        session = self.get_session()
        try:
            recommendation = Recommendation(**recommendation_data)
            session.add(recommendation)
            session.commit()
            session.refresh(recommendation)
            return recommendation
        finally:
            session.close()

    def get_latest_sensor_data(self, limit=10):
        """Get most recent sensor readings"""
        session = self.get_session()
        try:
            data = (
                session.query(SensorData)
                .order_by(SensorData.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [d.to_dict() for d in data]
        finally:
            session.close()

    def get_latest_recommendations(self, limit=10):
        """Get most recent recommendations"""
        session = self.get_session()
        try:
            recs = (
                session.query(Recommendation)
                .order_by(Recommendation.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [r.to_dict() for r in recs]
        finally:
            session.close()

    def get_sensor_data_by_id(self, sensor_id):
        """Get specific sensor reading by ID"""
        session = self.get_session()
        try:
            data = session.query(SensorData).filter(SensorData.id == sensor_id).first()
            return data.to_dict() if data else None
        finally:
            session.close()
