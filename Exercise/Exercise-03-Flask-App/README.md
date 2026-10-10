# Exercise 3: Deploy a Flask app on Minikube using kubectl and YAML

## Objective
Learn Kubernetes basics using Minikube to set up a single-node cluster and deploy a Python Flask application.

---

## Files in this Exercise
- `app.py`: Simple Flask web application running on port `15000`.
- `Dockerfile`: Container image definition based on `python:3.8-slim`.
- `flask-deployment-initial.yaml`: Initial Deployment manifest without Service.
- `flask-deployment.yaml`: Complete manifest with Deployment & NodePort Service (`port: 15000`, `targetPort: 15000`).

---

## Step-by-Step Execution Record

### Step 1: Start Minikube
```powershell
minikube start --driver=docker
```
**Status:** Single-node Minikube cluster started, node `minikube` is `Ready`.

### Step 2: Flask Application (`app.py`)
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask on Kubernetes!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000)
```

### Step 3: Dockerfile
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install flask
CMD ["python", "app.py"]
```

### Step 4: Build & Load Docker Image
```powershell
docker build -t flask-app:latest .
minikube image load flask-app:latest
```

### Step 5 & 6: Deploy Initial Application
```powershell
kubectl apply -f flask-deployment-initial.yaml
```
Output:
```
deployment.apps/flask-app created
```

### Step 7: Check Deployment Status
```powershell
kubectl get deployments
```
Output:
```
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
flask-app   1/1     1            1           3s
```

### Step 8: Verify Pods Created
```powershell
kubectl get pods -l app=flask-app
```
Output:
```
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-59f7cdccb4-mnp4j   1/1     Running   0          6s
```

### Step 9: Describe Deployment
```powershell
kubectl describe deployment flask-app
```
Key details:
- Replicas: 1 desired | 1 updated | 1 total | 1 available
- Container: `flask-app`, Image: `flask-app:latest`, Port: `15000/TCP`
- Conditions: `Available=True`, `Progressing=True`

### Step 10: View Deployment Logs
```powershell
kubectl logs flask-app-59f7cdccb4-mnp4j
```
Output:
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:15000
 * Running on http://10.244.0.3:15000
Press CTRL+C to quit
```

### Step 11: Check Services
```powershell
kubectl get services
```
Output:
```
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   2m4s
```
*(Notice that `flask-app-service` does not exist yet.)*

### Step 12: Try Accessing port 15000 Before Exposing Service
```bash
curl http://127.0.0.1:15000
```
Result: Fails with connection refused because Minikube runs inside a container network and the port is not yet exposed outside the pod.

### Step 13: Expose via Service in `flask-deployment.yaml`
Applied combined deployment and service:
```powershell
kubectl apply -f flask-deployment.yaml
```
Output:
```
deployment.apps/flask-app unchanged
service/flask-app-service created
```

Verified Services:
```
NAME                TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)           AGE
flask-app-service   NodePort    10.108.156.152   <none>        15000:30147/TCP   3s
kubernetes          ClusterIP   10.96.0.1        <none>        443/TCP           2m23s
```

### Accessing & Testing the Service
```bash
curl http://127.0.0.1:15000
```
**Response:**
```
Hello from Flask on Kubernetes!
```

---

## Questions & Answers

| Q# | Question | Answer |
|----|----------|--------|
| **Q1** | What is the purpose of `minikube service flask-app-service --url`? | To provide the URL for accessing the `flask-app-service` running in Minikube. |
| **Q2** | What happens when you run `minikube service flask-app-service --url`? | Minikube checks if the service is running, generates an access URL, and displays it in the terminal. |
| **Q3** | Why is `targetPort` used in Kubernetes Service configuration? | To specify the port number on which the container application is listening inside the Pod. |
| **Q4** | What is the difference between `port` and `targetPort`? | `port` is the exposed Service port; `targetPort` is the container port where traffic is forwarded. |
| **Q5** | How do you access a Flask application running in Minikube? | Use `minikube service <service-name> --url` or `kubectl port-forward`. |
| **Q6** | Why does the terminal need to remain open when using Docker driver on Linux/WSL? | Because the Docker driver requires an active terminal session to maintain the tunnel. |
| **Q7** | What is the benefit of using `--url` flag with minikube service? | It gives the exact URL string without attempting to launch an external web browser automatically. |
| **Q8** | What command is used to expose a service in Kubernetes? | `kubectl expose` or `kubectl apply -f <service.yaml>`. |
| **Q9** | How does Minikube help in local Kubernetes testing? | It runs a single-node Kubernetes cluster locally, allowing rapid testing without needing full cloud infrastructure. |
| **Q10**| What is the role of `kubectl` in this setup? | `kubectl` is the Kubernetes CLI used to deploy resources, view logs, inspect states, and manage the cluster. |
