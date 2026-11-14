
from simulator.fault_detector import detect_faults


def normal_data():
    return {
        "cooling_pump_status": "NORMAL",
        "battery_temperature": 30,
        "pressure": 2,
        "leak_detected": False
    }


def test_normal_operation():
    faults = detect_faults(normal_data())
    assert faults == []


def test_cooling_failure():
    data = normal_data()
    data["cooling_pump_status"] = "FAILED"

    faults = detect_faults(data)

    assert len(faults) == 1
    assert faults[0]["component"] == "Cooling System"
    assert faults[0]["severity"] == "CRITICAL"
    assert "Mini ROV" in faults[0]["recommendation"]


def test_battery_overheating():
    data = normal_data()
    data["battery_temperature"] = 80

    faults = detect_faults(data)

    assert len(faults) == 1
    assert faults[0]["problem"] == "Battery overheating"
    assert faults[0]["severity"] == "CRITICAL"


def test_high_pressure():
    data = normal_data()
    data["pressure"] = 8

    faults = detect_faults(data)

    assert len(faults) == 1
    assert faults[0]["component"] == "Pressure Sensor"
    assert faults[0]["severity"] == "WARNING"


def test_water_leak():
    data = normal_data()
    data["leak_detected"] = True

    faults = detect_faults(data)

    assert len(faults) == 1
    assert faults[0]["problem"] == "Water intrusion detected"
    assert faults[0]["severity"] == "CRITICAL"


def test_multiple_faults():
    data = normal_data()
    data["cooling_pump_status"] = "FAILED"
    data["battery_temperature"] = 80

    faults = detect_faults(data)

    assert len(faults) == 2

    components = [fault["component"] for fault in faults]

    assert "Cooling System" in components
    assert "Battery" in components
