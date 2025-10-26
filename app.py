from flask import Flask, request, jsonify
import math

app = Flask(__name__)

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

    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def nearest_neighbor(points, start_index=0):
    """Return nearest neighbor route order (list of indices)."""
    n = len(points)
    visited = [False] * n
    route = [start_index]
    visited[start_index] = True

    for _ in range(n - 1):
        last = route[-1]
        nearest = None
        min_dist = float('inf')
        for i, point in enumerate(points):
            if not visited[i]:
                dist = haversine(points[last], point)
                if dist < min_dist:
                    min_dist = dist
                    nearest = i
        route.append(nearest)
        visited[nearest] = True

    return route

# === ROUTE ===
@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()

    if not data or "locations" not in data:
        return jsonify({"message": "Send POST /optimize with JSON {locations:[{latitude,longitude}]}"}), 400

    locations = data["locations"]
    start_index = data.get("start_index", 0)

    # 🧹 Filter out empty or invalid coordinates
    cleaned = []
    for loc in locations:
        try:
            lat = float(loc["latitude"])
            lon = float(loc["longitude"])
            cleaned.append((lat, lon))
        except (TypeError, ValueError, KeyError):
            # Skip invalid or empty coordinates
            continue

    if not cleaned:
        return jsonify({"message": "No valid coordinates provided"}), 400

    # Ensure start_index is valid
    if start_index >= len(cleaned):
        start_index = 0

    route_order = nearest_neighbor(cleaned, start_index)
    ordered_points = [
        {"latitude": cleaned[i][0], "longitude": cleaned[i][1], "order": idx + 1}
        for idx, i in enumerate(route_order)
    ]

    return jsonify({
        "route": ordered_points,
        "route_order": route_order
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
