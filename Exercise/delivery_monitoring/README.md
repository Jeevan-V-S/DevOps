# Real-Time Operations Monitoring and Alerting (ZAPPTTO Delivery Service)

## Objective
As a DevOps engineer at ZAPPTTO, create a real-time operations monitoring and automated alerting stack for a fast-paced delivery service using:
- **Python (`delivery_metrics.py`)**: Simulates live delivery operations metrics exposed via `prometheus_client`.
- **Prometheus**: Scrapes operational metrics every interval and evaluates alert rules.
- **Grafana**: Visualizes metrics across operations dashboards.
- **Jenkins**: CI/CD automation pipeline (`Jenkinsfile`) for automated testing and container deployment.

---

## Directory Structure
```
delivery_monitoring/
├── delivery_metrics.py   # Python delivery metrics simulator
├── prometheus.yml        # Prometheus scrape configurations
├── alert_rules.yml       # Alerting rules (HighPendingDeliveries, HighAverageDeliveryTime)
├── Dockerfile            # Container definition for the metrics simulator
└── Jenkinsfile           # Jenkins CI/CD pipeline definition
```

---

## Live Endpoints & Verified Ports

| Service | Host URL | Description | Verified Status |
|---|---|---|---|
| **Delivery Metrics** | `http://localhost:8000/metrics` | Prometheus metrics endpoint | ✅ HTTP 200 OK |
| **Prometheus** | `http://localhost:9090` | Prometheus UI, Scrape Targets & Alerts | ✅ HTTP 200 OK |
| **Grafana** | `http://localhost:3000` | Analytics dashboards (`admin` / `admin`) | ✅ HTTP 200 OK |
| **Jenkins** | `http://localhost:8080` | Jenkins CI/CD Pipeline Automation | ✅ HTTP 200 OK |

**Jenkins Initial Admin Password:**
```
bbb0a530fe8e442489d7f60e65ad31e4
```

---

## Metric Definitions & Types

- **`total_deliveries` (Gauge)**: Total count of active deliveries in the pipeline.
- **`pending_deliveries` (Gauge)**: Deliveries waiting for driver assignment.
- **`on_the_way_deliveries` (Gauge)**: Deliveries currently in transit.
- **`average_delivery_time` (Summary)**: Observed delivery durations in seconds (`_count` and `_sum`).

Sample metrics scraped:
```
# HELP total_deliveries Total number of deliveries
# TYPE total_deliveries gauge
total_deliveries 70.0

# HELP pending_deliveries Number of pending deliveries
# TYPE pending_deliveries gauge
pending_deliveries 15.0

# HELP on_the_way_deliveries Number of deliveries on the way
# TYPE on_the_way_deliveries gauge
on_the_way_deliveries 18.0

# HELP average_delivery_time Average delivery time in seconds
# TYPE average_delivery_time summary
average_delivery_time_count 17.0
average_delivery_time_sum 460.76
```

---

## Configured Alerts (`alert_rules.yml`)

1. **`HighPendingDeliveries` (Warning)**:
   - **Expression**: `pending_deliveries > 10` for 15s
   - **Summary**: High pending deliveries
   - **Status**: Verified active & pending/firing when orders exceed 10.
2. **`HighAverageDeliveryTime` (Critical)**:
   - **Expression**: `(average_delivery_time_sum / average_delivery_time_count) > 30`
   - **Summary**: High average delivery time
   - **Status**: Verified **firing** on Prometheus when average delivery duration exceeds 30 seconds.

Verified Prometheus Alert API response:
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "labels": {"alertname": "HighPendingDeliveries", "severity": "warning"},
        "state": "pending"
      },
      {
        "labels": {"alertname": "HighAverageDeliveryTime", "severity": "critical"},
        "state": "firing"
      }
    ]
  }
}
```

---

## Steps to Reproduce / Run

### 1. Run Python Metrics Simulator:
```powershell
pip install prometheus-client
python delivery_metrics.py
```

### 2. Run Prometheus:
```powershell
docker run -d --name prometheus -p 9090:9090 \
  -v "${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml" \
  -v "${PWD}/alert_rules.yml:/etc/prometheus/alert_rules.yml" \
  prom/prometheus
```

### 3. Run Grafana:
```powershell
docker run -d --name grafana -p 3000:3000 grafana/grafana
```
- Open `http://localhost:3000`
- Log in with `admin` / `admin`
- Add Prometheus Data Source (`http://host.docker.internal:9090` or `http://172.17.0.1:9090`)
- Create Dashboard panels for `total_deliveries`, `pending_deliveries`, `on_the_way_deliveries`, and `average_delivery_time`.

### 4. Run Jenkins:
```powershell
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins \
  -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```
- Open `http://localhost:8080`
- Unlock using password: `bbb0a530fe8e442489d7f60e65ad31e4`
- Create a Pipeline job using [`Jenkinsfile`](./Jenkinsfile).
