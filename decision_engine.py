"""
Decision Logic Engine for Smart Agriculture
Provides explainable recommendations based on sensor data
"""

from typing import Dict, Tuple


class CropProfile:
    """Define optimal conditions for different crop types"""

    def __init__(
        self,
        name: str,
        optimal_moisture: Tuple[float, float],
        optimal_temp: Tuple[float, float],
        optimal_humidity: Tuple[float, float],
    ):
        self.name = name
        self.optimal_moisture = optimal_moisture  # (min, max) percentage
        self.optimal_temp = optimal_temp  # (min, max) celsius
        self.optimal_humidity = optimal_humidity  # (min, max) percentage


# Predefined crop profiles (extensible)
CROP_PROFILES = {
    "tomato": CropProfile("Tomato", (60, 80), (18, 27), (60, 80)),
    "lettuce": CropProfile("Lettuce", (70, 85), (15, 20), (60, 75)),
    "wheat": CropProfile("Wheat", (40, 60), (15, 25), (50, 70)),
    "corn": CropProfile("Corn", (50, 70), (20, 30), (60, 80)),
    "default": CropProfile("Default Crop", (50, 75), (18, 28), (60, 80)),
}


class DecisionEngine:
    """
    Core decision logic for irrigation, fertilization, and alerts
    All decisions are explainable with clear reasoning
    """

    def __init__(self, crop_type: str = "default"):
        self.crop = CROP_PROFILES.get(crop_type.lower(), CROP_PROFILES["default"])

    def analyze_sensor_data(
        self, soil_moisture: float, temperature: float, humidity: float
    ) -> Dict:
        """
        Main analysis function that generates all recommendations

        Returns a dictionary with irrigation, fertilizer, and alert recommendations
        """
        irrigation = self._evaluate_irrigation(soil_moisture, temperature, humidity)
        fertilizer = self._evaluate_fertilizer(soil_moisture, temperature)
        alerts = self._evaluate_alerts(soil_moisture, temperature, humidity)

        return {"irrigation": irrigation, "fertilizer": fertilizer, "alerts": alerts}

    def _evaluate_irrigation(
        self, soil_moisture: float, temperature: float, humidity: float
    ) -> Dict:
        """
        Irrigation decision logic with explainable reasoning

        Decision factors:
        1. Soil moisture level vs optimal range
        2. Temperature impact on evaporation
        3. Humidity impact on water retention
        """
        min_moisture, max_moisture = self.crop.optimal_moisture
        reasoning_parts = []

        # Primary factor: soil moisture
        if soil_moisture < min_moisture:
            moisture_deficit = min_moisture - soil_moisture
            base_amount = moisture_deficit * 0.5  # 0.5 liters per % deficit per m²

            reasoning_parts.append(
                f"Soil moisture ({soil_moisture:.1f}%) is below optimal range "
                f"({min_moisture:.1f}-{max_moisture:.1f}%)"
            )

            # Secondary factor: temperature adjustment
            temp_min, temp_max = self.crop.optimal_temp
            if temperature > temp_max:
                temp_excess = temperature - temp_max
                adjustment = 1 + (
                    temp_excess * 0.05
                )  # 5% increase per degree above optimal
                base_amount *= adjustment
                reasoning_parts.append(
                    f"Temperature ({temperature:.1f}°C) is above optimal, "
                    f"increasing water need by {(adjustment - 1) * 100:.0f}%"
                )

            # Tertiary factor: humidity adjustment
            if humidity < 50:
                humidity_factor = 1.2
                base_amount *= humidity_factor
                reasoning_parts.append(
                    f"Low humidity ({humidity:.1f}%) increases evaporation, "
                    f"adjusting water amount by 20%"
                )

            return {
                "action": "water",
                "amount": round(base_amount, 2),
                "reasoning": ". ".join(reasoning_parts) + ".",
            }

        elif soil_moisture > max_moisture:
            reasoning_parts.append(
                f"Soil moisture ({soil_moisture:.1f}%) is above optimal range "
                f"({min_moisture:.1f}-{max_moisture:.1f}%)"
            )
            reasoning_parts.append(
                "Excess water can lead to root rot and nutrient leaching"
            )

            return {
                "action": "reduce",
                "amount": 0,
                "reasoning": ". ".join(reasoning_parts) + ".",
            }

        else:
            reasoning_parts.append(
                f"Soil moisture ({soil_moisture:.1f}%) is within optimal range "
                f"({min_moisture:.1f}-{max_moisture:.1f}%)"
            )

            return {
                "action": "no_action",
                "amount": 0,
                "reasoning": ". ".join(reasoning_parts) + ". No irrigation needed.",
            }

    def _evaluate_fertilizer(self, soil_moisture: float, temperature: float) -> Dict:
        """
        Fertilizer recommendation logic with explainable reasoning

        Decision factors:
        1. Soil moisture (must be adequate for nutrient uptake)
        2. Temperature (affects nutrient availability)
        3. Simple NPK recommendation based on growth stage proxy
        """
        reasoning_parts = []
        min_moisture, max_moisture = self.crop.optimal_moisture

        # Fertilizer is only effective with proper moisture
        if soil_moisture < min_moisture * 0.7:
            reasoning_parts.append(
                f"Soil moisture ({soil_moisture:.1f}%) is too low for effective "
                f"nutrient uptake"
            )
            reasoning_parts.append("Irrigate before applying fertilizer")

            return {
                "action": "no_action",
                "type": None,
                "reasoning": ". ".join(reasoning_parts) + ".",
            }

        # Check temperature for nutrient activity
        temp_min, temp_max = self.crop.optimal_temp
        if temperature < temp_min - 5:
            reasoning_parts.append(
                f"Temperature ({temperature:.1f}°C) is too low for active nutrient uptake"
            )

            return {
                "action": "no_action",
                "type": None,
                "reasoning": ". ".join(reasoning_parts) + ".",
            }

        # Basic NPK recommendation (in real system, would consider soil tests)
        if (
            min_moisture <= soil_moisture <= max_moisture
            and temp_min <= temperature <= temp_max
        ):
            reasoning_parts.append(
                f"Conditions are optimal for fertilizer application: "
                f"moisture at {soil_moisture:.1f}%, temperature at {temperature:.1f}°C"
            )
            reasoning_parts.append(
                "Balanced NPK (10-10-10) recommended for general growth"
            )

            return {
                "action": "apply",
                "type": "NPK 10-10-10 (Balanced)",
                "reasoning": ". ".join(reasoning_parts) + ".",
            }

        return {
            "action": "no_action",
            "type": None,
            "reasoning": "Monitor conditions before fertilizing.",
        }

    def _evaluate_alerts(
        self, soil_moisture: float, temperature: float, humidity: float
    ) -> Dict:
        """
        Generate alerts for critical conditions

        Alert levels: none, warning, critical
        """
        alerts = []
        alert_level = "none"

        min_moisture, max_moisture = self.crop.optimal_moisture
        temp_min, temp_max = self.crop.optimal_temp

        # Critical drought risk
        if soil_moisture < min_moisture * 0.5:
            alerts.append(
                f"CRITICAL: Severe drought risk! Soil moisture ({soil_moisture:.1f}%) "
                f"is critically low. Immediate irrigation required."
            )
            alert_level = "critical"

        # Warning drought risk
        elif soil_moisture < min_moisture * 0.7:
            alerts.append(
                f"WARNING: Drought risk detected. Soil moisture ({soil_moisture:.1f}%) "
                f"is approaching critical levels."
            )
            alert_level = "warning"

        # Overwatering risk
        if soil_moisture > max_moisture * 1.3:
            message = (
                f"CRITICAL: Overwatering detected! Soil moisture ({soil_moisture:.1f}%) "
                f"is excessively high. Risk of root rot and nutrient leaching."
            )
            alerts.append(message)
            alert_level = "critical"

        elif soil_moisture > max_moisture * 1.1:
            alerts.append(
                f"WARNING: Soil moisture ({soil_moisture:.1f}%) is above optimal. "
                f"Reduce irrigation."
            )
            if alert_level == "none":
                alert_level = "warning"

        # Temperature alerts
        if temperature > temp_max + 5:
            alerts.append(
                f"WARNING: High temperature stress ({temperature:.1f}°C). "
                f"Consider shade cloth or additional irrigation."
            )
            if alert_level == "none":
                alert_level = "warning"

        elif temperature < temp_min - 5:
            alerts.append(
                f"WARNING: Low temperature ({temperature:.1f}°C) may slow growth. "
                f"Consider frost protection if below 0°C."
            )
            if alert_level == "none":
                alert_level = "warning"

        # Combined stress factors
        if soil_moisture < min_moisture and temperature > temp_max and humidity < 50:
            alerts.append(
                "CRITICAL: Multiple stress factors detected (low moisture, high temp, low humidity). "
                "Immediate action required!"
            )
            alert_level = "critical"

        return {"level": alert_level, "messages": alerts}

    def change_crop_type(self, crop_type: str):
        """Allow dynamic crop type changes (extensibility feature)"""
        self.crop = CROP_PROFILES.get(crop_type.lower(), CROP_PROFILES["default"])
        return self.crop.name


# Utility function for easy integration
def get_recommendations(
    soil_moisture: float,
    temperature: float,
    humidity: float,
    crop_type: str = "default",
) -> Dict:
    """
    Convenience function to get all recommendations in one call
    """
    engine = DecisionEngine(crop_type)
    return engine.analyze_sensor_data(soil_moisture, temperature, humidity)
