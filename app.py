from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 3958.8
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def nearest_neighbor(points, start_index=0):
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

@app.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.get_json()
    if not data or 'locations' not in data:
        return jsonify({"error": "Missing 'locations' field"}), 400

    locations = data['locations']
    start_index = data.get('start_index', 0)

    try:
        coords = [(float(l['latitude']), float(l['longitude'])) for l in locations]
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Invalid location data"}), 400

    route_order = nearest_neighbor(coords, start_index)

    route_with_order = []
    for stop_num, idx in enumerate(route_order, start=1):
        loc = locations[idx].copy()
        loc["order"] = stop_num
        route_with_order.append(loc)

    return jsonify({
        "route_order": route_order,
        "route": route_with_order
    })

@app.route('/')
def home():
    return jsonify({"message": "Send POST /optimize with JSON {locations:[{latitude,longitude}]}"})

if __name__ == '__main__':
    app.run()
