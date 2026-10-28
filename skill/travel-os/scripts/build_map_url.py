#!/usr/bin/env python3
"""Build a shareable Google Maps directions URL without an API key."""

import argparse
from urllib.parse import urlencode


TRAVEL_MODES = {"driving", "walking", "bicycling", "transit"}


def build_place_url(location, city="", provider="google"):
    """Keyword search, not a verified POI or a coordinate conversion.

    Sources: developer.amap.com/api/uri-api/guide/search/search and
    developers.google.com/maps/documentation/urls/get-started (2026-10-27).
    """
    if not location.strip():
        raise ValueError("location is required")
    if provider == "amap":
        query = {"keyword": location.strip(), "city": city.strip(),
                 "view": "list", "src": "TravelOS", "callnative": "0"}
        return "https://uri.amap.com/search?" + urlencode(query)
    if provider == "google":
        query = {"api": "1", "query": " ".join(filter(None, [city.strip(), location.strip()]))}
        return "https://www.google.com/maps/search/?" + urlencode(query)
    raise ValueError("unsupported map provider")


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
