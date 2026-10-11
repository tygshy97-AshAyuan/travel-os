#!/usr/bin/env python3
"""Build a shareable Google Maps directions URL without an API key."""

import argparse
from urllib.parse import urlencode


TRAVEL_MODES = {"driving", "walking", "bicycling", "transit"}


def build_directions_url(origin, destination, waypoints=(), travel_mode="driving"):
    if not origin.strip() or not destination.strip():
        raise ValueError("origin and destination are required")
    if travel_mode not in TRAVEL_MODES:
        raise ValueError(f"unsupported travel mode: {travel_mode}")
    query = {
        "api": "1",
        "origin": origin.strip(),
        "destination": destination.strip(),
        "travelmode": travel_mode,
    }
    cleaned_waypoints = [waypoint.strip() for waypoint in waypoints if waypoint.strip()]
    if cleaned_waypoints:
        query["waypoints"] = "|".join(cleaned_waypoints)
    return f"https://www.google.com/maps/dir/?{urlencode(query)}"


def main():
    parser = argparse.ArgumentParser(description="Build a Travel OS directions URL")
    parser.add_argument("origin")
    parser.add_argument("destination")
    parser.add_argument("--waypoint", action="append", default=[])
    parser.add_argument("--mode", choices=sorted(TRAVEL_MODES), default="driving")
    args = parser.parse_args()
    print(
        build_directions_url(
            args.origin,
            args.destination,
            waypoints=args.waypoint,
            travel_mode=args.mode,
        )
    )


if __name__ == "__main__":
    main()
