
import math
from enum import Enum


class MissionState(Enum):
    DOCKED = "DOCKED"
    DEPLOYING = "DEPLOYING"
    INSPECTING = "INSPECTING"
    RETURNING = "RETURNING"
    MISSION_COMPLETE = "MISSION_COMPLETE"
    SUBMARINE_MOVING = "SUBMARINE_MOVING"


class MiniROVSimulation:

    SCENARIOS = {
        "Minor corrosion": {
            "target": "Hull plating",
            "severity": 3,
            "confidence": 90,
            "delay_risk": 2,
            "deployment_risk": 3,
            "finding": "Minor corrosion detected. No immediate critical threat."
        },
        "Critical propulsion obstruction": {
            "target": "Propulsion system",
            "severity": 9,
            "confidence": 95,
            "delay_risk": 9,
            "deployment_risk": 3,
            "finding": "Critical obstruction detected near the propulsion system."
        },
        "Uncertain sensor anomaly": {
            "target": "Rear hull / sensor area",
            "severity": 7,
            "confidence": 35,
            "delay_risk": 7,
            "deployment_risk": 4,
            "finding": "Potential anomaly detected, but sensor confidence is low."
        }
    }

    def __init__(self):

        self.state = MissionState.DOCKED

        self.main_auv_position = (0.0, 0.0, 0.0)
        self.start_position = (0.0, 0.0, 0.0)
        self.docking_position = (0.0, -1.0, 0.0)
        self.deployment_position = (0.0, -3.0, 0.0)

        self.position = self.docking_position

        self.waypoint_offsets = [
            (4.0, 2.0, -3.0),
            (7.0, 5.0, -4.0),
            (3.0, 8.0, -2.0)
        ]

        # Corrected: show the planned inspection route before deployment.
        self.waypoints = list(self.waypoint_offsets)

        self.current_waypoint = 0
        self.speed = 0.5

        self.battery = 100.0
        self.battery_usage = 0.1

        self.inspection_progress = 0
        self.inspection_records = []

        self.total_steps = 0
        self.position_history = [self.position]

        self.connected = True
        self.submarine_moving = False

        self.selected_scenario = "Critical propulsion obstruction"
        self.decision = self.evaluate_inspection_need(
            self.selected_scenario
        )

        self.inspection_target = "Not selected"

        self.submarine_destination = (12.0, 10.0, 0.0)

    # --------------------------------------------------
    # AI INSPECTION NECESSITY ENGINE
    # --------------------------------------------------

    def evaluate_inspection_need(self, scenario_name=None):

        if scenario_name is None:
            scenario_name = self.selected_scenario

        scenario = self.SCENARIOS[scenario_name]

        severity = scenario["severity"]
        confidence = scenario["confidence"] / 100.0
        delay_risk = scenario["delay_risk"]
        deployment_risk = scenario["deployment_risk"]

        anomaly_risk_score = (
            severity * confidence * (0.5 + delay_risk / 20)
        )

        deployment_cost = (
            deployment_risk * 0.8
            + (100 - self.battery) / 25
            + 2
        )

        if self.battery < 30 and severity >= 6:
            decision = "ESCALATE"

        elif severity >= 6 and confidence < 0.50:
            decision = "ESCALATE"

        elif (
            anomaly_risk_score >= deployment_cost + 2
            and self.battery >= 30
        ):
            decision = "DEPLOY"

        else:
            decision = "MONITOR"

        return {
            "decision": decision,
            "anomaly_risk_score": round(anomaly_risk_score, 2),
            "deployment_cost": round(deployment_cost, 2),
            "severity": severity,
            "confidence": scenario["confidence"],
            "delay_risk": delay_risk,
            "deployment_risk": deployment_risk,
            "target": scenario["target"]
        }

    def select_inspection_scenario(self, scenario_name):

        if scenario_name not in self.SCENARIOS:
            raise ValueError("Unknown inspection scenario.")

        if self.state not in (
            MissionState.DOCKED,
            MissionState.MISSION_COMPLETE
        ):
            return

        self.selected_scenario = scenario_name
        self.inspection_target = self.SCENARIOS[scenario_name]["target"]
        self.decision = self.evaluate_inspection_need(scenario_name)

    # --------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------

    def move_towards(self, target):

        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        dz = target[2] - self.position[2]

        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance <= self.speed:
            self.position = target
            return True

        ratio = self.speed / distance

        self.position = (
            self.position[0] + dx * ratio,
            self.position[1] + dy * ratio,
            self.position[2] + dz * ratio
        )

        return False

    # --------------------------------------------------
    # DEPLOYMENT
    # --------------------------------------------------

    def start_deployment(self, scenario_name=None, operator_override=False):

        if self.state not in (
            MissionState.DOCKED,
            MissionState.MISSION_COMPLETE
        ):
            return False

        if scenario_name is not None:
            self.selected_scenario = scenario_name

        # A fresh demonstration starts from the original submarine position.
        if self.state == MissionState.MISSION_COMPLETE:
            self.main_auv_position = (0.0, 0.0, 0.0)

        # Reset mission resources before evaluating a fresh mission.
        self.battery = 100.0
        self.position = self.docking_position
        self.start_position = self.main_auv_position

        self.decision = self.evaluate_inspection_need(
            self.selected_scenario
        )

        if self.decision["decision"] != "DEPLOY" and not operator_override:
            return False

        self.waypoints = [
            (
                self.start_position[0] + point[0],
                self.start_position[1] + point[1],
                self.start_position[2] + point[2]
            )
            for point in self.waypoint_offsets
        ]

        self.docking_position = (
            self.start_position[0],
            self.start_position[1] - 1.0,
            self.start_position[2]
        )

        self.deployment_position = (
            self.start_position[0],
            self.start_position[1] - 3.0,
            self.start_position[2]
        )

        self.position = self.docking_position

        self.current_waypoint = 0
        self.inspection_progress = 0
        self.inspection_records = []
        self.total_steps = 0
        self.position_history = [self.position]

        self.connected = True
        self.submarine_moving = False
        self.inspection_target = self.SCENARIOS[
            self.selected_scenario
        ]["target"]

        self.state = MissionState.DEPLOYING

        return True

    # --------------------------------------------------
    # INSPECTION
    # --------------------------------------------------

    def record_inspection(self):

        scenario = self.SCENARIOS[self.selected_scenario]

        record = {
            "target": scenario["target"],
            "scenario": self.selected_scenario,
            "finding": scenario["finding"],
            "severity": scenario["severity"],
            "confidence": scenario["confidence"]
        }

        self.inspection_records.append(record)

        self.inspection_progress += 1

    # --------------------------------------------------
    # RETURN AND RECONNECTION
    # --------------------------------------------------

    def return_to_docking_position(self):

        self.state = MissionState.RETURNING

    # --------------------------------------------------
    # MAIN SIMULATION LOOP
    # --------------------------------------------------

    def advance(self):

        if self.state == MissionState.DOCKED:
            return

        if self.state == MissionState.MISSION_COMPLETE:
            return

        if self.state == MissionState.SUBMARINE_MOVING:

            dx = self.submarine_destination[0] - self.main_auv_position[0]
            dy = self.submarine_destination[1] - self.main_auv_position[1]
            dz = self.submarine_destination[2] - self.main_auv_position[2]

            distance = math.sqrt(dx**2 + dy**2 + dz**2)

            if distance <= 0.2:
                self.main_auv_position = self.submarine_destination
                self.state = MissionState.MISSION_COMPLETE
                self.submarine_moving = False
                return

            ratio = 0.2 / distance

            self.main_auv_position = (
                self.main_auv_position[0] + dx * ratio,
                self.main_auv_position[1] + dy * ratio,
                self.main_auv_position[2] + dz * ratio
            )

            return

        self.total_steps += 1

        self.battery = max(
            0.0,
            self.battery - self.battery_usage
        )

        # Step 1: Mini ROV completely detaches from submarine.
        if self.state == MissionState.DEPLOYING:

            if self.move_towards(self.deployment_position):
                self.connected = False
                self.state = MissionState.INSPECTING

        # Step 2: Mini ROV independently inspects targets.
        elif self.state == MissionState.INSPECTING:

            if self.current_waypoint < len(self.waypoints):

                target = self.waypoints[self.current_waypoint]

                if self.move_towards(target):

                    self.record_inspection()
                    self.current_waypoint += 1

            else:
                self.return_to_docking_position()

        # Step 3: Mini ROV returns to submarine.
        elif self.state == MissionState.RETURNING:

            if self.move_towards(self.docking_position):

                self.position = self.docking_position
                self.connected = True

                self.state = MissionState.SUBMARINE_MOVING
                self.submarine_moving = True

        self.position_history.append(self.position)

    # --------------------------------------------------
    # STATUS FOR DASHBOARD
    # --------------------------------------------------

    def get_status(self):

        return {
            "state": self.state.value,
            "position": self.position,
            "main_auv_position": self.main_auv_position,
            "battery": round(self.battery, 2),
            "inspection_progress": self.inspection_progress,
            "current_waypoint": self.current_waypoint,
            "total_waypoints": len(self.waypoints),
            "inspection_records": self.inspection_records,
            "total_steps": self.total_steps,
            "mission_complete": (
                self.state == MissionState.MISSION_COMPLETE
            ),
            "position_history": self.position_history,
            "connected": self.connected,
            "submarine_moving": self.submarine_moving,
            "scenario": self.selected_scenario,
            "inspection_target": self.inspection_target,
            "decision": self.decision
        }
