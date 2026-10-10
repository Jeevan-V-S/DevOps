# Exercise 1: Hello Pod — Kubernetes

## Business Scenario

As a DevOps Engineer at Zepto, I deployed a lightweight storefront web application using the Nginx container image on Kubernetes and verified it is running and accessible.

---

## Environment

| Component        | Details                        |
|-----------------|-------------------------------|
| OS              | Windows 11 (WSL2 backend)     |
| Docker Desktop  | 29.4.1 (context: desktop-linux) |
| kubectl         | v1.34.1                       |
| Minikube        | v1.39.0                       |
| Kubernetes      | v1.37.0                       |
| Driver          | Docker                        |

---

## Steps Performed

### Step 1: Prerequisites Check

```powershell
kubectl version --client
# Client Version: v1.34.1

minikube version
# minikube version: v1.39.0

docker version
# Docker Engine: 29.4.1
```

> Minikube was not installed and was downloaded to `C:\Users\jeeva\bin\minikube.exe` and added to user PATH.

---

### Step 2: Start Kubernetes Cluster

```powershell
minikube start --driver=docker
```

**Output:** Cluster started successfully with `kicbase` Docker image pulled (507 MB).

```powershell
kubectl get nodes
```

```
NAME       STATUS   ROLES           AGE     VERSION
minikube   Ready    control-plane   6m30s   v1.37.0
```

✅ Node status: **Ready**

---

### Step 3: Deploy the Nginx Pod

```powershell
kubectl run hello-k8s --image=nginx --port=80
```

```
pod/hello-k8s created
```

```powershell
kubectl get pods
```

```
NAME        READY   STATUS    RESTARTS   AGE
hello-k8s   1/1     Running   0          47s
```

✅ Pod status: **Running**

---

### Step 4: Expose the Application

```powershell
kubectl expose pod hello-k8s --type=NodePort --port=80
```

```
service/hello-k8s exposed
```

```powershell
kubectl get services
```

```
NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
hello-k8s    NodePort    10.104.154.217   <none>        80:31798/TCP   0s
kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP        2m27s
```

✅ Service created with NodePort **31798**

---

### Step 5: Access the Application

On Windows with Docker driver (WSL2), `minikube service --url` requires an open terminal tunnel.  
Used `kubectl port-forward` to make Nginx accessible on `localhost:8080`:

```powershell
kubectl port-forward pod/hello-k8s 8080:80
```

Tested with curl:
```
curl http://localhost:8080
```

**Result:** HTTP 200 OK — Nginx welcome page returned successfully.

```
< HTTP/1.1 200 OK
< Server: nginx/1.31.6
< Content-Type: text/html
< Content-Length: 896
```

✅ Nginx welcome page: **accessible**

---

### Step 6: Final Verification

#### `minikube status`
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

#### `kubectl get nodes`
```
NAME       STATUS   ROLES           AGE     VERSION
minikube   Ready    control-plane   6m30s   v1.37.0
```

#### `kubectl get pods -o wide`
```
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
hello-k8s   1/1     Running   0          5m    10.244.0.3   minikube   <none>           <none>
```

#### `kubectl get services`
```
NAME         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
hello-k8s    NodePort    10.104.154.217   <none>        80:31798/TCP   4m
kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP        6m27s
```

#### `kubectl describe pod hello-k8s` (summary)
```
Name:       hello-k8s
Namespace:  default
Node:       minikube/192.168.49.2
Status:     Running
IP:         10.244.0.3
Image:      nginx
Port:       80/TCP
Ready:      True
Events:
  Pulling image "nginx"         → Pulled in 20.79s
  Container created and started
```

---

## Concepts Explained

### Pod
A **Pod** is the smallest deployable unit in Kubernetes. It wraps one or more containers that share network and storage. Here, `hello-k8s` is a Pod containing one Nginx container.

### Container Image (`nginx`)
The **`nginx` Docker image** is the official lightweight web server image from Docker Hub. It serves static HTML over HTTP on port 80. Kubernetes pulls this image automatically when creating the Pod.

### Service
A **Service** is a stable network endpoint that exposes one or more Pods. Without a Service, Pods are only reachable within the cluster. The Service provides a fixed IP and port even if Pods are recreated.

### NodePort
**NodePort** is a Service type that exposes the application on a specific port of the cluster node (here port `31798`). It enables external access to the application from outside the cluster.

---

## Summary

✅ Kubernetes cluster started with Minikube  
✅ Nginx Pod deployed and running  
✅ NodePort Service created  
✅ Application accessible via `kubectl port-forward` at `http://localhost:8080`  
✅ Nginx welcome page confirmed HTTP 200 OK
