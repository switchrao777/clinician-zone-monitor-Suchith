# clinician-zone-monitor-Suchith

Clinician Safety Zone Monitor:

This project basically implements a monitoring service that tracks clinician locations and sends an email alert when a clinician leaves their assigned safety zone.

The system polls a GeoJSON API, determines whether each clinician is inside their designated polygon, and triggers alerts when they move outside.

How It Works:

The monitor runs continuously and performs the following steps:

Polls the clinician status API every 30 seconds.

Extracts the clinician’s location and safety zone from the GeoJSON response.

Uses a ray-casting algorithm to determine whether the clinician is inside the polygon.

Sends an email alert when a clinician transitions from in-zone to out-of-zone.

Boundary points are treated as outside the zone.

If the API fails to return valid data, the cycle is skipped without generating alerts.

Design Choices:

Polling interval: 30 seconds provides fast detection while keeping API usage low.

State tracking: Alerts are only sent on status changes to prevent duplicates.

Robustness: Invalid or missing API responses are safely ignored.

Setup:

Install dependencies:

pip install requests

Configure environment variables:

export SMTP_USER="your_email@gmail.com"
export SMTP_PASS="your_app_password"
export FROM_EMAIL="your_email@gmail.com"
export TO_EMAIL="recipient_email@gmail.com"

Run the monitor:

python monitor.py
Testing

Clinician ID 7 is a permanent test clinician that is always outside the safety zone.

Author

Suchith Rao
University of Maryland – Computer Science
