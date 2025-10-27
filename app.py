from flask import Flask, request, jsonify
import math
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask app is running on Render!", 200


# === CONFIG ===
HO_LATITUDE = 42.553203
HO_LONGITUDE = -82.9336493
HO_COORD = (HO_LATITUDE, HO_LONGITUDE)


# === FUNCTIONS ===
def haversine(coord1, coord2):
    """Calculate straight-line distance between two (lat, lng) points in miles."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 3958.8  # Radius of Earth in miles

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def nearest_neighbor(points, start_coord):
    """Return nearest neighbor route order (list of indices) starting from HQ, but HQ is not in result."""
    n = len(points)
    visited = [False] * n
    route = []
    current_coord = start_coord

    for _ in range(n):
        nearest = None
        min_dist = float('inf')
        for i, point in enumerate(points):
            if not visited[i]:
                dist = haversine(current_coord, point)
                if dist < min_dist:
                    min_dist = dist
                    nearest = i
        route.append(nearest)
        visited[nearest] = True
        current_coord = points[nearest]

    return route


# === ROUTE ===
@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()

    if not data or "locations" not in data:
        return jsonify({"message": "Send POST /optimize with JSON {locations:[{latitude,longitude}]}"}), 400

    locations = data["locations"]

    # 🧹 Filter out invalid coordinates
    cleaned = []
    for loc in locations:
        try:
            lat = float(loc["latitude"])
            lon = float(loc["longitude"])
            cleaned.append((lat, lon))
        except (TypeError, ValueError, KeyError):
            continue

    if not cleaned:
        return jsonify({"message": "No valid coordinates provided"}), 400

    # 🚀 Compute route starting from HQ (but exclude HQ from output)
    route_order = nearest_neighbor(cleaned, HO_COORD)

    # 🔢 Build ordered response list
    ordered_points = [
        {
            "latitude": cleaned[i][0],
            "longitude": cleaned[i][1],
            "order": idx + 1
        }
        for idx, i in enumerate(route_order)
    ]

    return jsonify({
        "route": ordered_points,
        "route_order": route_order
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
