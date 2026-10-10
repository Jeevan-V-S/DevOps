# Exercise 2: Multi-Node Kubernetes Cluster with Multiple Applications and ReplicaSets

## Business Scenario & Storyboard
In an e-commerce platform:
- **Product Catalog (AppA)**: Provides information about available products (2 replicas).
- **Shopping Cart (AppB)**: Manages user shopping carts (3 replicas).

To ensure high availability and fault tolerance, replicas of both services are distributed across multiple nodes using `podAntiAffinity` rules with `topologyKey: "kubernetes.io/hostname"`. If any single node goes down, the services remain resilient and uninterrupted.

---

## Environment
- **Operating System**: Windows 11 (WSL2 backend)
- **Minikube Profile**: `devops-multinode` (3 nodes)
- **Nodes**: `devops-multinode` (control-plane), `devops-multinode-m02` (worker), `devops-multinode-m03` (worker)
- **Container Runtime**: containerd on Docker Desktop

---

## Steps Executed & Verified

### Step 0: Clean up any existing cluster
```powershell
minikube stop
minikube delete
```

### Step 1: Multi-Node Setup & Registry Add-on
```powershell
minikube start --nodes 3 -p devops-multinode --driver=docker --force
minikube -p devops-multinode addons enable registry
```

### Step 2 & 3: Application Code
- `product_catalog.py`: Flask app exposing `/products` on port 80.
- `shopping_cart.py`: Flask app exposing GET `/cart` and POST `/cart` on port 80.

### Step 4: Dockerization
- Created `Dockerfile.product` and `Dockerfile.shopping` based on `python:3.9-slim`.
- Built Docker images:
```powershell
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .
```

### Step 5: Image Loading to Minikube
```powershell
minikube -p devops-multinode image load product-catalog:latest
minikube -p devops-multinode image load shopping-cart:latest
```

### Step 6 & 7: Kubernetes Deployments & Services
Applied manifests with `podAntiAffinity`:
```powershell
kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml
kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml
```

### Step 8: Verification of Pod Distribution Across Nodes
```powershell
kubectl get pods -o wide
```
**Actual Output:**
```
NAME                             READY   STATUS    RESTARTS   AGE   IP           NODE                   NOMINATED NODE   READINESS GATES
product-catalog-7cb85d4f-95nhw   1/1     Running   0          25s   10.244.1.4   devops-multinode-m02   <none>           <none>
product-catalog-7cb85d4f-dvj6k   1/1     Running   0          25s   10.244.2.3   devops-multinode-m03   <none>           <none>
shopping-cart-6858b5f797-24cxm   1/1     Running   0          24s   10.244.0.4   devops-multinode       <none>           <none>
shopping-cart-6858b5f797-6xhmw   1/1     Running   0          24s   10.244.2.4   devops-multinode-m03   <none>           <none>
shopping-cart-6858b5f797-cwmjs   1/1     Running   0          24s   10.244.1.5   devops-multinode-m02   <none>           <none>
```

Pod placement breakdown:
- **Product Catalog (2 replicas)**: `devops-multinode-m02` and `devops-multinode-m03`
- **Shopping Cart (3 replicas)**: `devops-multinode`, `devops-multinode-m02`, and `devops-multinode-m03`

### Step 9 & 10: Access & Testing Endpoints
Forwarded ports to test locally:
- Product Catalog service on port `35855`
- Shopping Cart service on port `38975`

#### 1. Retrieve Product List
```bash
curl http://127.0.0.1:35855/products
```
**Response:**
```json
[{"id":1,"name":"Laptop","price":1200},{"id":2,"name":"Phone","price":800},{"id":3,"name":"Headphones","price":150}]
```

#### 2. Retrieve Empty Cart
```bash
curl http://127.0.0.1:38975/cart
```
**Response:**
```json
[]
```

#### 3. Add Item to Cart
```bash
curl -X POST http://127.0.0.1:38975/cart -H "Content-Type: application/json" -d '{"id": 1, "name": "Laptop", "quantity": 1}'
```
**Response:**
```json
[{"id":1,"name":"Laptop","quantity":1}]
```

#### 4. Verify Updated Cart
```bash
curl http://127.0.0.1:38975/cart
```
**Response:**
```json
[{"id":1,"name":"Laptop","quantity":1}]
```

---

## Summary
The multi-node cluster ensures high availability and resilience. By leveraging `podAntiAffinity` rules, pods for both the Product Catalog and Shopping Cart services are evenly scheduled across different nodes, eliminating single points of failure.
