import numpy as np
from datetime import datetime


BUILDING_FLOODED = 1
ROAD_FLOODED = 3

SEGMENTATION_CLASS_NAMES = {
    0: "Background",
    1: "Building Flooded",
    2: "Building Non-Flooded",
    3: "Road Flooded",
    4: "Road Non-Flooded",
    5: "Water",
    6: "Tree",
    7: "Vehicle",
    8: "Pool",
    9: "Grass"
}


def calculate_segmentation_areas(predicted_mask):
    total_pixels = predicted_mask.size

    if total_pixels == 0:
        return {
            "flooded_building_area": 0.0,
            "flooded_road_area": 0.0,
            "flood_coverage": 0.0
        }

    building_pixels = np.count_nonzero(
        predicted_mask == BUILDING_FLOODED
    )

    road_pixels = np.count_nonzero(
        predicted_mask == ROAD_FLOODED
    )

    building_area = building_pixels / total_pixels * 100
    road_area = road_pixels / total_pixels * 100
    coverage = (building_pixels + road_pixels) / total_pixels * 100

    return {
        "flooded_building_area": float(building_area),
        "flooded_road_area": float(road_area),
        "flood_coverage": float(coverage)
    }


def get_detected_regions(predicted_mask):
    regions = []

    for class_id, class_name in SEGMENTATION_CLASS_NAMES.items():
        if np.any(predicted_mask == class_id):
            if class_id != 0:
                regions.append(class_name)

    return regions


def calculate_severity(
    flood_detected,
    flood_coverage,
    flooded_building_area,
    flooded_road_area
):
    if not flood_detected:
        return "LOW"

    if (
        flood_coverage >= 40
        or flooded_road_area >= 30
        or flooded_building_area >= 30
    ):
        return "HIGH"

    if (
        flood_coverage >= 15
        or flooded_road_area >= 10
        or flooded_building_area >= 10
    ):
        return "MEDIUM"

    return "LOW"


def calculate_rescue_priority(
    flood_detected,
    people_count,
    vehicle_count,
    severity,
    flooded_road_area
):
    if not flood_detected:
        return "NO IMMEDIATE ACTION"

    if people_count >= 5:
        return "IMMEDIATE"

    if severity == "HIGH" and people_count > 0:
        return "IMMEDIATE"

    if severity == "HIGH" and flooded_road_area >= 30:
        return "HIGH"

    if people_count > 0:
        return "HIGH"

    if severity == "MEDIUM":
        return "HIGH"

    if vehicle_count > 0:
        return "MEDIUM"

    return "LOW"


def generate_situation_summary(
    flood_detected,
    flood_probability,
    flood_coverage,
    flooded_building_area,
    flooded_road_area,
    people_count,
    vehicle_count,
    severity
):
    if not flood_detected:
        return (
            "The current AI analysis did not identify significant "
            "flood impact in the analyzed aerial image."
        )

    impact_parts = []

    if flooded_building_area > 0:
        impact_parts.append(
            f"{flooded_building_area:.2f}% building impact"
        )

    if flooded_road_area > 0:
        impact_parts.append(
            f"{flooded_road_area:.2f}% road impact"
        )

    if not impact_parts:
        impact_parts.append(
            f"{flood_coverage:.2f}% total flood impact"
        )

    impact_text = " and ".join(impact_parts)

    return (
        f"Flooding was detected with a "
        f"{flood_probability * 100:.2f}% model probability. "
        f"The segmentation model estimates {impact_text}. "
        f"Detected people: {people_count}; detected vehicles: "
        f"{vehicle_count}. Current project-defined severity is {severity}."
    )


def generate_recommended_action(
    flood_detected,
    severity,
    rescue_priority,
    people_count,
    flooded_building_area,
    flooded_road_area
):
    if not flood_detected:
        return (
            "Continue routine monitoring and reassess if new aerial "
            "imagery indicates changing conditions."
        )

    if people_count > 0:
        return (
            "Prioritize review of detected people locations and "
            "coordinate appropriate emergency response."
        )

    if severity == "HIGH":
        return (
            "Prioritize field assessment of the affected flooded "
            "road and building areas and review access conditions."
        )

    if severity == "MEDIUM":
        return (
            "Inspect the affected road and building regions and "
            "consider additional drone imagery for confirmation."
        )

    if flooded_road_area > 0 or flooded_building_area > 0:
        return (
            "Monitor the identified flooded regions and obtain "
            "additional imagery if conditions change."
        )

    return (
        "Continue monitoring and obtain additional imagery for confirmation."
    )


def generate_assessment(
    flood_detected,
    flood_probability,
    predicted_mask,
    people_count,
    vehicle_count
):
    areas = calculate_segmentation_areas(predicted_mask)

    flooded_building_area = areas["flooded_building_area"]
    flooded_road_area = areas["flooded_road_area"]
    flood_coverage = areas["flood_coverage"]

    severity = calculate_severity(
        flood_detected,
        flood_coverage,
        flooded_building_area,
        flooded_road_area
    )

    rescue_priority = calculate_rescue_priority(
        flood_detected,
        people_count,
        vehicle_count,
        severity,
        flooded_road_area
    )

    detected_regions = get_detected_regions(predicted_mask)

    situation_summary = generate_situation_summary(
        flood_detected,
        flood_probability,
        flood_coverage,
        flooded_building_area,
        flooded_road_area,
        people_count,
        vehicle_count,
        severity
    )

    recommended_action = generate_recommended_action(
        flood_detected,
        severity,
        rescue_priority,
        people_count,
        flooded_building_area,
        flooded_road_area
    )

    timestamp = datetime.now().strftime(
        "%d %b %Y, %I:%M:%S %p"
    )

    return {
        "report_title": "DroneRescue Incident Assessment",
        "analysis_timestamp": timestamp,
        "flood_detected": "YES" if flood_detected else "NO",
        "flood_probability": round(flood_probability * 100, 2),
        "people_visible": int(people_count),
        "vehicles_visible": int(vehicle_count),
        "flood_coverage": round(flood_coverage, 2),
        "flooded_building_area": round(flooded_building_area, 2),
        "flooded_road_area": round(flooded_road_area, 2),
        "flood_severity": severity,
        "rescue_priority": rescue_priority,
        "detected_regions": detected_regions,
        "situation_summary": situation_summary,
        "recommended_action": recommended_action,
        "assessment_note": (
            "Severity and rescue priority are project-defined "
            "assessment rules and are not official emergency-service directives."
        )
    }


def print_assessment(report):
    print("\nDroneRescue Emergency Assessment")
    print(f"Flood Detected        : {report['flood_detected']}")
    print(f"Flood Probability     : {report['flood_probability']}%")
    print(f"People Visible        : {report['people_visible']}")
    print(f"Vehicles Visible      : {report['vehicles_visible']}")
    print(f"Flood Coverage        : {report['flood_coverage']}%")
    print(f"Flooded Building Area : {report['flooded_building_area']}%")
    print(f"Flooded Road Area     : {report['flooded_road_area']}%")
    print(f"Flood Severity        : {report['flood_severity']}")
    print(f"Rescue Priority       : {report['rescue_priority']}")
    print(f"Situation Summary     : {report['situation_summary']}")
    print(f"Recommended Action    : {report['recommended_action']}")
