# Exercise 5: Docker Networking with Multiple Containers

## Objective
Understand Docker networking concepts and configure a multi-container application communicating over a custom user-defined bridge network.

---

## Scenario
A multi-tier architecture consisting of:
- **Container 1 (`flask`)**: Python Flask REST API web server
- **Container 2 (`mysql`)**: MySQL Database
- **Container 3 (`redis`)**: Redis Cache

---

## Files in this Exercise
- `app.py`: Flask application exposing `/about` on port `5001`.
- `requirements.txt`: Python package dependencies (`Flask>=2.0.1`).
- `Dockerfile`: Container image based on `python:3.9-slim` with `iputils-ping` installed for ICMP connectivity testing.

---

## Step-by-Step Task Execution

### Task 1: Create a Bridge Network
```powershell
docker network create --driver bridge my-bridge-net
```
**Output:**
```
a5444fb15325303128c04a152bd3af3b07f05fa1fa87079866560b8791c768c5
```

### Task 2: Verify the Network
```powershell
docker network ls
```
**Output:**
```
NETWORK ID     NAME            DRIVER    SCOPE
a5444fb15325   my-bridge-net   bridge    local
```

### Task 3: Inspect the Network
```powershell
docker network inspect my-bridge-net
```
**Output (Key details):**
- Subnet: `172.18.0.0/16`
- Gateway: `172.18.0.1`
- Driver: `bridge`, Scope: `local`

### Task 4: Launch Containers
Built the Flask image:
```powershell
docker build -t flask-api .
```

Started all three containers on `my-bridge-net`:
```powershell
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=rootpassword mysql:latest
docker run -d --name redis --net=my-bridge-net redis:latest
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api
```

Verified running containers:
```
CONTAINER ID   IMAGE          COMMAND                  STATUS          PORTS                    NAMES
381aba64c028   flask-api      "python app.py"          Up 5 seconds    0.0.0.0:5001->5001/tcp   flask
b04e5a6bd5e5   redis:latest   "docker-entrypoint.s…"   Up 6 seconds    6379/tcp                 redis
7f2537af1e9c   mysql:latest   "docker-entrypoint.s…"   Up 23 seconds   3306/tcp, 33060/tcp      mysql
```

### Task 5: Test Connectivity
Tested DNS resolution and ICMP ping from the `flask` container using container names:

#### 1. Ping MySQL (`ping mysql`):
```bash
docker exec flask ping -c 3 mysql
```
```
PING mysql (172.18.0.2) 56(84) bytes of data.
64 bytes from mysql.my-bridge-net (172.18.0.2): icmp_seq=1 ttl=64 time=0.944 ms
64 bytes from mysql.my-bridge-net (172.18.0.2): icmp_seq=2 ttl=64 time=0.184 ms
64 bytes from mysql.my-bridge-net (172.18.0.2): icmp_seq=3 ttl=64 time=0.103 ms

--- mysql ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2022ms
```
✅ **0% packet loss** — resolved `mysql` to `172.18.0.2`.

#### 2. Ping Redis (`ping redis`):
```bash
docker exec flask ping -c 3 redis
```
```
PING redis (172.18.0.3) 56(84) bytes of data.
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=1 ttl=64 time=1.47 ms
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=2 ttl=64 time=0.108 ms
64 bytes from redis.my-bridge-net (172.18.0.3): icmp_seq=3 ttl=64 time=0.092 ms

--- redis ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2006ms
```
✅ **0% packet loss** — resolved `redis` to `172.18.0.3`.

#### 3. Test Flask `/about` Endpoint from Host:
```bash
curl http://localhost:5001/about
```
```json
{
  "description": "This is a simple REST API built with Flask.",
  "name": "Simple REST API",
  "version": "1.0"
}
```

### Task 6: Clean Up
```powershell
docker stop mysql redis flask
docker rm mysql redis flask
docker network rm my-bridge-net
```
✅ All containers stopped and removed. Custom bridge network removed cleanly.

---

## Questions & Answers

| Question | Answer |
|---|---|
| **What is the purpose of the `--net` flag in `docker run`?** | The `--net` (or `--network`) flag specifies which network the container should connect to, enabling it to join a shared network with other containers and use automatic DNS resolution. |
| **How do containers communicate with each other on the same network?** | On user-defined bridge networks, Docker provides embedded DNS resolution. Containers can communicate directly using **container names** (e.g., `mysql`, `redis`) or their assigned IP addresses. |
| **What is the difference between a bridge network and a host network?** | • **Bridge Network**: Provides network virtualization and isolation. Containers have private IP addresses and communicate through a software bridge/gateway.<br>• **Host Network**: Removes network isolation between container and Docker host; container binds directly to host network interfaces and ports without NAT. |
| **How can you expose a container's port to the host machine?** | Use the `-p` or `--publish` flag (e.g. `-p 5001:5001`), which creates port-mapping/NAT from the host port to the container port. |
