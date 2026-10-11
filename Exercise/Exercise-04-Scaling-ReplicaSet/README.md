# Exercise 4: Scaling Flask App on Single Node using ReplicaSets

## Real-Life Tech Use Case: E-commerce Flash Sale
During a flash sale on an e-commerce platform (like Flipkart's Big Billion Days or Amazon Prime Day):
- A standard service handles regular load on 3 Pods.
- During traffic spikes (e.g. 10,000 req/min), the system scales horizontally to 5 or more Pods running identical application replicas.
- If any Pod crashes under pressure or fails its health check, Kubernetes automatically restarts or replaces it without downtime.
- Requests are load balanced across active Pods.

---

## Files in this Exercise
- `app.py`: Flask application featuring `/`, `/buy` (order simulation with hostname tracking), and `/health` (liveness/readiness probes).
- `Dockerfile`: Container image definition based on `python:3.11-slim` running via Gunicorn.
- `flashsale-replicaset.yaml`: Kubernetes `ReplicaSet` (initial replicas: 3) and `ClusterIP` Service with probes and resource limits.

---

## Step-by-Step Execution Record

### Step 1 & 2: Minikube Single-Node Cluster Verification
```powershell
kubectl get nodes
```
Output:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   16h   v1.37.0
```

### Step 3: Application Code & Dockerization
- Created `app.py` with `/`, `/buy`, and `/health` endpoints.
- Built Docker image `flashsale:1.0` and loaded into Minikube:
```powershell
docker build -t flashsale:1.0 .
minikube image load flashsale:1.0
```

### Step 4: Apply ReplicaSet & Service
```powershell
kubectl apply -f flashsale-replicaset.yaml
```
Output:
```
replicaset.apps/flashsale-rs created
service/flashsale-svc created
```

### Step 5 & 6: Verify Initial Pods (3 Replicas)
```powershell
kubectl get rs
```
```
NAME           DESIRED   CURRENT   READY   AGE
flashsale-rs   3         3         3       20s
```

```powershell
kubectl get pods -o wide
```
```
NAME                 READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
flashsale-rs-52mj5   1/1     Running   0          20s   10.244.0.6   minikube   <none>           <none>
flashsale-rs-k6bdt   1/1     Running   0          20s   10.244.0.4   minikube   <none>           <none>
flashsale-rs-p6vsk   1/1     Running   0          20s   10.244.0.5   minikube   <none>           <none>
```

### Step 7: Scale ReplicaSet to 5 Replicas
```powershell
kubectl scale rs flashsale-rs --replicas=5
```
Output:
```
replicaset.apps/flashsale-rs scaled
```

### Step 8 & 9: Verify Scaled ReplicaSet & 5 Pods
```powershell
kubectl get rs
```
```
NAME           DESIRED   CURRENT   READY   AGE
flashsale-rs   5         5         5       62s
```

```powershell
kubectl get pods -o wide
```
```
NAME                 READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
flashsale-rs-52mj5   1/1     Running   0          62s   10.244.0.6   minikube   <none>           <none>
flashsale-rs-dds6h   1/1     Running   0          26s   10.244.0.7   minikube   <none>           <none>
flashsale-rs-k6bdt   1/1     Running   0          62s   10.244.0.4   minikube   <none>           <none>
flashsale-rs-p6vsk   1/1     Running   0          62s   10.244.0.5   minikube   <none>           <none>
flashsale-rs-pr29g   1/1     Running   0          26s   10.244.0.8   minikube   <none>           <none>
```
*All 5 pods scheduled on `minikube` node and reached `1/1 Running` status.*

### Step 10: Delete One Pod (Simulate Pod Crash/Failure)
```powershell
kubectl delete pod flashsale-rs-52mj5
```
Output:
```
pod "flashsale-rs-52mj5" deleted from default namespace
```

### Step 11: Verify Self-Healing (Automatic Pod Replacement)
```powershell
kubectl get pods -o wide
```
```
NAME                 READY   STATUS    RESTARTS   AGE    IP           NODE       NOMINATED NODE   READINESS GATES
flashsale-rs-dds6h   1/1     Running   0          80s    10.244.0.7   minikube   <none>           <none>
flashsale-rs-k6bdt   1/1     Running   0          116s   10.244.0.4   minikube   <none>           <none>
flashsale-rs-p6vsk   1/1     Running   0          116s   10.244.0.5   minikube   <none>           <none>
flashsale-rs-pr29g   1/1     Running   0          80s    10.244.0.8   minikube   <none>           <none>
flashsale-rs-wlt57   1/1     Running   0          26s    10.244.0.9   minikube   <none>           <none>
```
*The ReplicaSet immediately detected the missing pod and created a replacement pod (`flashsale-rs-wlt57`) within seconds, maintaining the desired count of 5.*

### Step 12: Endpoint Verifications
- **Homepage (`GET /`)**:
  ```json
  {"message":"Welcome to Big Sale!","pod":"flashsale-rs-p6vsk","ts":1791702902.430977}
  ```
- **Flash Sale Order (`GET /buy?user=customer101`)**:
  ```json
  {"item":"Laptop","served_by_pod":"flashsale-rs-p6vsk","status":"success","time":"07:15:02","user":"customer101"}
  ```
- **Health Check (`GET /health`)**:
  ```json
  {"pod":"flashsale-rs-p6vsk","status":"healthy"}
  ```

---

## Questions & Answers

| Q# | Question | Answer |
|---|---|---|
| **Q1** | What is the initial number of replicas in the ReplicaSet? | **3** |
| **Q2** | How many pods are running after applying the ReplicaSet configuration? | **3** |
| **Q3** | What happens when you scale the ReplicaSet to 5 replicas? | Kubernetes creates **2 additional pods** to match the desired replica count of 5. The ReplicaSet then manages 5 active running pods. |
| **Q4** | What happens when you delete one pod? | Kubernetes automatically detects that the active count (4) is less than the desired count (5) and immediately creates a replacement pod (`flashsale-rs-wlt57`), maintaining zero service disruption. |
| **Q5** | How does Kubernetes maintain the desired number of replicas? | The **ReplicaSet controller** continuously runs a reconciliation loop comparing the current cluster state (`spec.selector`) to the desired state (`spec.replicas`). It creates or terminates pods as needed to match the specification. |
| **Q6** | How many nodes are running? | **1** (`minikube`) |
| **Q7** | Where are the pods running with respect to nodes? | All 5 pods run on the single node `minikube`: <br>• Pod 1: `flashsale-rs-dds6h` on `minikube` (IP: 10.244.0.7)<br>• Pod 2: `flashsale-rs-k6bdt` on `minikube` (IP: 10.244.0.4)<br>• Pod 3: `flashsale-rs-p6vsk` on `minikube` (IP: 10.244.0.5)<br>• Pod 4: `flashsale-rs-pr29g` on `minikube` (IP: 10.244.0.8)<br>• Pod 5: `flashsale-rs-wlt57` on `minikube` (IP: 10.244.0.9) |
