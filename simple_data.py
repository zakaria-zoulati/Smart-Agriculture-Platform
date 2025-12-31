#!/usr/bin/env python3
"""
Sample Data Generator for Smart Agriculture Platform
Creates realistic test data to demonstrate the system
"""

import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:8000/api/sensor-data"


def generate_sensor_reading(scenario="normal"):
    """
    Generate realistic sensor data based on scenario

    Scenarios:
    - normal: Optimal conditions
    - drought: Low moisture, high temp
    - overwater: Excessive moisture
    - hot_day: High temperature stress
    - cold_night: Low temperature
    """

    scenarios = {
        "normal": {
            "soil_moisture": (60, 75),
            "temperature": (20, 26),
            "humidity": (60, 75),
        },
        "drought": {
            "soil_moisture": (25, 40),
            "temperature": (30, 38),
            "humidity": (30, 45),
        },
        "overwater": {
            "soil_moisture": (85, 95),
            "temperature": (18, 24),
            "humidity": (80, 95),
        },
        "hot_day": {
            "soil_moisture": (45, 60),
            "temperature": (32, 40),
            "humidity": (35, 50),
        },
        "cold_night": {
            "soil_moisture": (55, 70),
            "temperature": (8, 15),
            "humidity": (70, 85),
        },
    }

    ranges = scenarios.get(scenario, scenarios["normal"])

    return {
        "soil_moisture": round(random.uniform(*ranges["soil_moisture"]), 1),
        "temperature": round(random.uniform(*ranges["temperature"]), 1),
        "humidity": round(random.uniform(*ranges["humidity"]), 1),
        "location": "Field-1",
        "crop_type": random.choice(["tomato", "lettuce", "wheat", "corn"]),
    }


def send_reading(data):
    """Send a sensor reading to the API"""
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend API")
        print("   Make sure the backend is running: python backend.py")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def generate_sample_data():
    """Generate a set of sample readings"""
    print("=" * 60)
    print("🌱 Smart Agriculture - Sample Data Generator")
    print("=" * 60)
    print()

    scenarios = [
        ("normal", "Normal conditions"),
        ("normal", "Normal conditions"),
        ("drought", "Drought stress"),
        ("overwater", "Overwatering"),
        ("hot_day", "Hot day stress"),
        ("cold_night", "Cold night"),
        ("normal", "Recovery to normal"),
        ("normal", "Optimal conditions"),
    ]

    print(f"Generating {len(scenarios)} sample readings...\n")

    success_count = 0
    for i, (scenario, description) in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] Generating: {description}")

        data = generate_sensor_reading(scenario)
        print(
            f"    📊 Moisture: {data['soil_moisture']:.1f}% | "
            f"Temp: {data['temperature']:.1f}°C | "
            f"Humidity: {data['humidity']:.1f}%"
        )

        result = send_reading(data)

        if result and result.get("success"):
            rec = result["recommendations"]
            print(f"    💡 Action: {rec['irrigation_action']}")
            print(f"    🚨 Alert: {rec['alert_level']}")
            success_count += 1
        else:
            print(f"    ❌ Failed to send reading")

        print()
        time.sleep(0.5)  # Small delay between requests

    print("=" * 60)
    print(f"✅ Successfully generated {success_count}/{len(scenarios)} readings")
    print("=" * 60)
    print("\n📊 View the results in the dashboard:")
    print("   http://localhost:8501")
    print()


def interactive_mode():
    """Interactive mode for manual data entry"""
    print("=" * 60)
    print("🌱 Smart Agriculture - Interactive Data Entry")
    print("=" * 60)
    print()

    while True:
        print("\nChoose a scenario:")
        print("1. Normal conditions")
        print("2. Drought stress")
        print("3. Overwatering")
        print("4. Hot day")
        print("5. Cold night")
        print("6. Custom values")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "7":
            print("\n👋 Goodbye!")
            break

        scenario_map = {
            "1": "normal",
            "2": "drought",
            "3": "overwater",
            "4": "hot_day",
            "5": "cold_night",
        }

        if choice == "6":
            # Custom values
            try:
                print("\nEnter custom values:")
                moisture = float(input("Soil Moisture (0-100%): "))
                temp = float(input("Temperature (-20 to 60°C): "))
                humidity = float(input("Humidity (0-100%): "))

                data = {
                    "soil_moisture": moisture,
                    "temperature": temp,
                    "humidity": humidity,
                    "location": "Field-1",
                    "crop_type": "default",
                }
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
                continue

        elif choice in scenario_map:
            data = generate_sensor_reading(scenario_map[choice])
            print(f"\n📊 Generated data:")
            print(f"   Moisture: {data['soil_moisture']:.1f}%")
            print(f"   Temperature: {data['temperature']:.1f}°C")
            print(f"   Humidity: {data['humidity']:.1f}%")

        else:
            print("❌ Invalid choice. Please try again.")
            continue

        # Send the data
        print("\n📤 Sending data to API...")
        result = send_reading(data)

        if result and result.get("success"):
            rec = result["recommendations"]
            print("\n✅ Data submitted successfully!")
            print("\n💧 IRRIGATION:")
            print(f"   Action: {rec['irrigation_action']}")
            if rec["irrigation_amount"]:
                print(f"   Amount: {rec['irrigation_amount']} liters/m²")
            print(f"   Reason: {rec['irrigation_reasoning']}")

            print("\n🌾 FERTILIZER:")
            print(f"   Action: {rec['fertilizer_action']}")
            if rec["fertilizer_type"]:
                print(f"   Type: {rec['fertilizer_type']}")
            print(f"   Reason: {rec['fertilizer_reasoning']}")

            print(f"\n🚨 ALERT LEVEL: {rec['alert_level'].upper()}")
            if rec["alert_message"]:
                print(f"   {rec['alert_message']}")
        else:
            print("\n❌ Failed to submit data")


def main():
    """Main entry point"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        print("Usage:")
        print("  python sample_data.py              # Generate sample dataset")
        print("  python sample_data.py --interactive # Interactive mode")
        print()

        response = input("Generate sample data? (y/n): ")
        if response.lower() == "y":
            generate_sample_data()
        else:
            print("Run with --interactive for manual data entry")


if __name__ == "__main__":
    main()
