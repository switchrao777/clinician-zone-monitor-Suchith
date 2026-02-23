import os
import smtplib
from email.message import EmailMessage
import time
import requests

BASE =  "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test"
CLINICIAN_IDS =  [1, 2, 3, 4, 5, 6]
POLL_SECONDS =  30

def fetch(cid):

    try:
        r =  requests.get(f"{BASE}/clinicianstatus/{cid}", timeout=5)
        r.raise_for_status()
        return r.json()
    
    except Exception:

        return None


def extract_point_and_polygon(geojson):

    if not isinstance(geojson, dict):
        return None

    features = geojson.get("features")
    if not isinstance(features, list):
        return None

    point =  None

    polygon = None

    for f in features:
        geom = f.get("geometry", {})

        if geom.get("type") == "Point":
            point = geom.get("coordinates")
        elif geom.get("type") == "Polygon":

            polygon = geom.get("coordinates")

    if not point or not polygon:
        return None

    lon, lat = map(float, point)

    ring = polygon[0]

    return (lon, lat), ring

def point_on_segment(p, a, b, eps=1e-12):
    x, y = p
    x1, y1 = a
    x2, y2 = b

    cross = (x - x1)*(y2 - y1) - (y - y1)*(x2 - x1)

    if abs(cross) > eps:
        return False

    return (
        min(x1, x2) - eps <= x <= max(x1, x2) + eps
        and min(y1, y2) - eps <= y <= max(y1, y2) + eps
    )


def point_in_polygon_strict(point, ring):

    ring = [(float(x), float(y))  for x, y in ring]
    p = (float(point[0]), float(point[1]))

    if ring[0] != ring[-1]:

        ring.append(ring[0])

    for i in range(len(ring)-1):
        if point_on_segment(p, ring[i], ring[i+1]):
            return False

    x, y = p
    inside = False

    for i in range(len(ring)-1):
        x1, y1 = ring[i]
        x2, y2 = ring[i+1]

        if (y1 > y) != (y2 > y):
            x_intersect = x1 + (y - y1)*(x2 - x1)/(y2 - y1)
            if x_intersect > x:
                inside = not inside

    return inside


def send_email(cid, point):

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Clinician out of zone: {cid}"

        msg["From"] = os.environ["SMTP_USER"]

        msg["To"] = os.environ["TO_EMAIL"]

        msg.set_content(
            f"Clinician {cid} is OUT of their safety zone.\n\n"

            f"Coordinates: {point}"
        )

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as s:
            s.starttls()

            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])

            s.send_message(msg)

        print("EMAIL SENT ->", cid)

    except Exception as e:

        print("EMAIL FAILED:", e)


def monitor_forever():

    last_status = {cid: None for cid in CLINICIAN_IDS}

    cached_ring = None

    while True:

        for cid in CLINICIAN_IDS:

            data = fetch(cid)
            if not data:
                continue

            result = extract_point_and_polygon(data)
            if not result:
                continue

            point, ring = result

            in_zone = point_in_polygon_strict(point, ring)

            prev = last_status[cid]
            last_status[cid] = in_zone

            print(f"Clinician {cid}: in_zone={in_zone}")

           
            if (prev is None and in_zone is False) or (prev is True and in_zone is False):
                send_email(cid, point)

        print("-"*40)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    monitor_forever()