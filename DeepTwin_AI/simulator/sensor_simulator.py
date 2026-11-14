
import random
import time
from datetime import datetime


def generate_sensor_data(scenario="normal"):
    """Generate simulated underwater vehicle sensor readings."""

    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "battery_level": round(random.uniform(65, 95), 1),
        "battery_temperature": round(random.uniform(25, 35), 1),
        "pressure": round(random.uniform(1.0, 3.0), 2),
        "leak_detected": False,
        "scenario": scenario,
        "cooling_pump_status": "NORMAL",
    }

    if scenario == "battery_overheat":
        data["battery_temperature"] = round(random.uniform(65, 85), 1)

    
    elif scenario == "cooling_fault":
        data["battery_temperature"] = round(random.uniform(70, 90), 1)
        data["cooling_pump_status"] = "FAILED"


    elif scenario == "pressure_fault":
        data["pressure"] = round(random.uniform(7.0, 10.0), 2)

    elif scenario == "water_leak":
        data["leak_detected"] = True

    return data


if __name__ == "__main__":
    scenarios = [
        "normal",
        "battery_overheat",
        "pressure_fault",
        "water_leak",
    ]

    for scenario in scenarios:
        reading = generate_sensor_data(scenario)
        print(f"\nScenario: {scenario}")
        print(reading)
        time.sleep(1)
