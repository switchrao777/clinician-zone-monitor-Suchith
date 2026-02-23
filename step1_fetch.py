import requests

BASE = "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test"

def fetch(clinician_id):
    url = f"{BASE}/clinicianstatus/{clinician_id}"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()

def extract_point_and_polygon(geojson):
    features = geojson["features"]

    point_coords = None
    polygon_coords = None

    for f in features:
        geom = f["geometry"]

        if geom["type"] == "Point":

            point_coords = geom["coordinates"]        
        elif geom["type"] == "Polygon":

            polygon_coords = geom["coordinates"]      

    if point_coords  is None or   polygon_coords is None:
        raise ValueError("Missing Point or Polygon")

    lon  =  float(point_coords[0])

    lat =  float(point_coords[1])

    ring  =  polygon_coords[0]
    return  (lon, lat), ring

def point_on_segment(p, a, b, eps=1e-12):

    x, y = p
    x1, y1 = a
    x2, y2 =.  b

    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > eps:

        return False

    if min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps:

        return True
    
    return False

def point_in_polygon_strict(point, ring):

    ring = [(float(x), float(y)) for x, y in ring]

    p = (float(point[0]), float(point[1]))

    if ring[0] != ring[-1]:

        ring.append(ring[0])

    
    for i in range(len(ring) - 1):
        
        if point_on_segment(p, ring[i], ring[i + 1]):
            return False

    x, y = p
    inside = False
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]

        crosses = (y1 > y) != (y2 > y)
        if crosses:
            x_at_y = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x_at_y > x:
                inside = not inside

    return inside

if __name__ == "__main__":
    clinician_id = 7
    geojson = fetch(clinician_id)

    if "features" not in geojson:
        print("Non-GeoJSON response:", geojson)
    else:
        point, ring = extract_point_and_polygon(geojson)
        in_zone = point_in_polygon_strict(point, ring)
        print("Clinician:", clinician_id)
        print("Point (lon,lat):", point)
        print("Strictly inside zone?", in_zone)