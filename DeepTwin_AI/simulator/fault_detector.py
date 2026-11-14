
def detect_faults(data):
    faults = []

    if data.get("cooling_pump_status") == "FAILED":
        faults.append({
            "component": "Cooling System",
            "severity": "CRITICAL",
            "problem": "Cooling system failure",
            "recommendation": (
                "Inspect the cooling pump, coolant circulation, "
                "and temperature sensors. Deploy the Mini ROV "
                "for a visual inspection."
            )
        })


    if data["battery_temperature"] > 60:
        faults.append({
            "component": "Battery",
            "severity": "CRITICAL",
            "problem": "Battery overheating",
            "recommendation": "Inspect battery cooling and power systems."
        })

    if data["pressure"] > 6:
        faults.append({
            "component": "Pressure Sensor",
            "severity": "WARNING",
            "problem": "Abnormally high pressure reading",
            "recommendation": "Verify sensor calibration and inspect operating depth."
        })

    if data["leak_detected"]:
        faults.append({
            "component": "Hull",
            "severity": "CRITICAL",
            "problem": "Water intrusion detected",
            "recommendation": "Inspect seals and waterproof compartments."
        })

    return faults


if __name__ == "__main__":
    from sensor_simulator import generate_sensor_data

    scenarios = [
        "normal",
        "battery_overheat",
        "pressure_fault",
        "water_leak"
    ]

    for scenario in scenarios:
        data = generate_sensor_data(scenario)
        faults = detect_faults(data)

        print(f"\nScenario: {scenario}")

        if faults:
            for fault in faults:
                print(f"FAULT: {fault['problem']}")
                print(f"Severity: {fault['severity']}")
                print(f"Action: {fault['recommendation']}")
        else:
            print("SYSTEM HEALTHY")
