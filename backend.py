"""
FastAPI Backend for Smart Agriculture Platform
Provides REST API endpoints for sensor data and recommendations
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from database import DatabaseManager
from decision_engine import get_recommendations, CROP_PROFILES

# Initialize FastAPI app
app = FastAPI(
    title="Smart Agriculture API",
    description="Backend API for smart agriculture monitoring and decision support",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = DatabaseManager()

# Pydantic models for request/response validation
class SensorDataInput(BaseModel):
    """Schema for incoming sensor data"""
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage")
    temperature: float = Field(..., ge=-20, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    location: Optional[str] = Field("Field-1", description="Location identifier")
    crop_type: Optional[str] = Field("default", description="Type of crop")


class SensorDataResponse(BaseModel):
    """Schema for sensor data response"""
    id: int
    timestamp: str
    soil_moisture: float
    temperature: float
    humidity: float
    location: str


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    id: int
    timestamp: str
    sensor_data_id: int
    irrigation_action: str
    irrigation_amount: Optional[float]
    irrigation_reasoning: str
    fertilizer_action: str
    fertilizer_type: Optional[str]
    fertilizer_reasoning: str
    alert_level: str
    alert_message: Optional[str]


# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Smart Agriculture API is running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/sensor-data", response_model=dict)
def submit_sensor_data(data: SensorDataInput):
    """
    Submit new sensor data and get immediate recommendations
    
    This endpoint:
    1. Stores sensor data in database
    2. Runs decision logic
    3. Stores recommendations
    4. Returns both sensor data and recommendations
    """
    try:
        # Store sensor data
        sensor_record = db.add_sensor_data(
            soil_moisture=data.soil_moisture,
            temperature=data.temperature,
            humidity=data.humidity,
            location=data.location
        )
        
        # Get recommendations from decision engine
        analysis = get_recommendations(
            soil_moisture=data.soil_moisture,
            temperature=data.temperature,
            humidity=data.humidity,
            crop_type=data.crop_type
        )
        
        # Prepare recommendation data for storage
        recommendation_data = {
            'sensor_data_id': sensor_record.id,
            'irrigation_action': analysis['irrigation']['action'],
            'irrigation_amount': analysis['irrigation']['amount'],
            'irrigation_reasoning': analysis['irrigation']['reasoning'],
            'fertilizer_action': analysis['fertilizer']['action'],
            'fertilizer_type': analysis['fertilizer']['type'],
            'fertilizer_reasoning': analysis['fertilizer']['reasoning'],
            'alert_level': analysis['alerts']['level'],
            'alert_message': ' | '.join(analysis['alerts']['messages']) if analysis['alerts']['messages'] else None
        }
        
        # Store recommendation
        recommendation_record = db.add_recommendation(recommendation_data)
        
        return {
            "success": True,
            "sensor_data": sensor_record.to_dict(),
            "recommendations": recommendation_record.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sensor data: {str(e)}")


@app.get("/api/sensor-data/latest", response_model=List[dict])
def get_latest_sensor_data(limit: int = 10):
    """
    Get the most recent sensor readings
    
    Query params:
    - limit: Number of records to return (default: 10)
    """
    try:
        data = db.get_latest_sensor_data(limit=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor data: {str(e)}")


@app.get("/api/sensor-data/{sensor_id}", response_model=dict)
def get_sensor_data_by_id(sensor_id: int):
    """Get specific sensor data by ID"""
    try:
        data = db.get_sensor_data_by_id(sensor_id)
        if data is None:
            raise HTTPException(status_code=404, detail="Sensor data not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor data: {str(e)}")


@app.get("/api/recommendations/latest", response_model=List[dict])
def get_latest_recommendations(limit: int = 10):
    """
    Get the most recent recommendations
    
    Query params:
    - limit: Number of records to return (default: 10)
    """
    try:
        recommendations = db.get_latest_recommendations(limit=limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")


@app.post("/api/analyze", response_model=dict)
def analyze_conditions(data: SensorDataInput):
    """
    Analyze sensor conditions without storing data
    Useful for what-if scenarios and testing
    """
    try:
        analysis = get_recommendations(
            soil_moisture=data.soil_moisture,
            temperature=data.temperature,
            humidity=data.humidity,
            crop_type=data.crop_type
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "input": data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing conditions: {str(e)}")


@app.get("/api/crops", response_model=dict)
def get_available_crops():
    """
    Get list of available crop profiles
    Demonstrates extensibility of the system
    """
    crops = {
        name: {
            "name": profile.name,
            "optimal_moisture": profile.optimal_moisture,
            "optimal_temperature": profile.optimal_temp,
            "optimal_humidity": profile.optimal_humidity
        }
        for name, profile in CROP_PROFILES.items()
    }
    
    return {
        "success": True,
        "crops": crops
    }


@app.get("/api/stats", response_model=dict)
def get_statistics():
    """
    Get basic statistics about the system
    """
    try:
        latest_sensors = db.get_latest_sensor_data(limit=100)
        latest_recommendations = db.get_latest_recommendations(limit=100)
        
        # Calculate some basic stats
        if latest_sensors:
            avg_moisture = sum(s['soil_moisture'] for s in latest_sensors) / len(latest_sensors)
            avg_temp = sum(s['temperature'] for s in latest_sensors) / len(latest_sensors)
            avg_humidity = sum(s['humidity'] for s in latest_sensors) / len(latest_sensors)
        else:
            avg_moisture = avg_temp = avg_humidity = 0
        
        # Count alerts
        alert_counts = {
            'critical': sum(1 for r in latest_recommendations if r['alert_level'] == 'critical'),
            'warning': sum(1 for r in latest_recommendations if r['alert_level'] == 'warning'),
            'none': sum(1 for r in latest_recommendations if r['alert_level'] == 'none')
        }
        
        return {
            "success": True,
            "total_readings": len(latest_sensors),
            "total_recommendations": len(latest_recommendations),
            "averages": {
                "soil_moisture": round(avg_moisture, 2),
                "temperature": round(avg_temp, 2),
                "humidity": round(avg_humidity, 2)
            },
            "alert_counts": alert_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)