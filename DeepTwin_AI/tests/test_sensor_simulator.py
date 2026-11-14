
from simulator.sensor_simulator import generate_sensor_data


def test_normal_simulation():
    data = generate_sensor_data("normal")

    assert isinstance(data, dict)
    assert data["scenario"] == "normal"
    assert data["cooling_pump_status"] == "NORMAL"
    assert data["leak_detected"] is False


def test_cooling_fault_simulation():
    data = generate_sensor_data("cooling_fault")

    assert data["scenario"] == "cooling_fault"
    assert data["cooling_pump_status"] == "FAILED"



def test_battery_overheat_simulation():
    data = generate_sensor_data("battery_overheat")

    assert data["scenario"] == "battery_overheat"
    assert 65 <= data["battery_temperature"] <= 85


def test_pressure_fault_simulation():
    data = generate_sensor_data("pressure_fault")

    assert data["scenario"] == "pressure_fault"
    assert 7 <= data["pressure"] <= 10


def test_water_leak_simulation():
    data = generate_sensor_data("water_leak")

    assert data["scenario"] == "water_leak"
    assert data["leak_detected"] is True
