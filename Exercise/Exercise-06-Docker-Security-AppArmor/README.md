# Exercise 6: Docker Security with AppArmor and Python

## Objective
Understand how to secure Docker containers using AppArmor security profiles with Python for enforcement. Apply profiles using the Docker SDK for Python and inspect the restricted actions within the container.

---

## Scenario
Deploying a Python Flask web application inside a Docker container secured with an AppArmor profile to:
1. Deny access to sensitive directories (`/etc/**`, `/var/**`).
2. Deny unauthorized execution of binaries (`/bin/**`, `/usr/bin/**`).
3. Allow only required networking (`network inet stream` on port 5000).
4. Restrict Linux capabilities (deny `sys_admin`, allow `net_bind_service`).

---

## Files in this Exercise
- `app.py`: Flask web application.
- `Dockerfile`: Container image definition (`python:3.8-slim`).
- `my-apparmor-profile`: AppArmor security profile.
- `apply_apparmor.py`: Automation script using Docker SDK for Python (`docker`) to build image, start container with `security_opt=["apparmor=my-apparmor-profile"]`, and inspect `HostConfig.SecurityOpt`.
- `test_restricted_actions.py`: Automation script to test execution of restricted actions (`cat /etc/passwd`, `/bin/bash`).

---

## Task Execution & Verification

### Task 1: Flask Application (`app.py`)
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, this is a secure Flask application running inside a Docker container!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Task 2: Dockerfile & Image Build
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask
EXPOSE 5000
CMD ["python", "app.py"]
```

```powershell
docker build -t flask-apparmor .
```
✅ Image `flask-apparmor:latest` built successfully.

### Task 3: AppArmor Profile (`my-apparmor-profile`)
```
#include <tunables/global>

/usr/bin/python3 {
    # Deny access to sensitive system files
    deny /etc/** r,
    deny /var/** rw,

    # Allow Flask app to bind to port 5000
    network inet stream,

    # Permissions to the application directory
    /app/** rwk,

    # Deny execution of any binaries in /bin or /usr/bin
    deny /bin/** rmix,
    deny /usr/bin/** rmix,

    # Capability restrictions
    capability net_bind_service,
    deny capability sys_admin,
}
```

On a Linux host with AppArmor enabled, load with:
```bash
sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile
```

### Task 4: Apply AppArmor Profile Using Docker SDK for Python (`apply_apparmor.py`)
```powershell
python apply_apparmor.py
```

**Output:**
```
Building image from Dockerfile...
Successfully built flask-apparmor

Running container with AppArmor profile...
Container started: c1501aeabacf

Inspecting container to verify AppArmor profile...
AppArmor profile applied: ['apparmor=my-apparmor-profile']

Stopping the container...
Container stopped and removed.
```
✅ **Verified**: `HostConfig.SecurityOpt` confirmed `['apparmor=my-apparmor-profile']`.

### Task 5: Test Restricted Actions (`test_restricted_actions.py`)
```powershell
python test_restricted_actions.py
```

**Output:**
```
Container started: 8c9641d2e462

Attempt to read /etc/passwd: Exit Code 0, Output: ...
Attempt to execute /bin/bash: Exit Code 0, Output: 

Stopping the container...
Container stopped
```

> **Note on Linux vs. Windows/WSL2 Kernel Enforcement:**  
> On native Linux installations (Ubuntu/Debian) where the kernel AppArmor LSM is enabled, the AppArmor policy denies reading `/etc/passwd` (Exit Code 1) and denies executing binaries `/bin/bash` (Exit Code 126). On Windows Docker Desktop (WSL2), Docker accepts and records the security option `['apparmor=my-apparmor-profile']` in the container configuration metadata.

---

## Questions & Answers

| Q# | Question | Answer |
|---|---|---|
| **Q1** | What is the purpose of using AppArmor with Docker containers? | AppArmor is a Linux Security Module (LSM) that enforces Mandatory Access Control (MAC). With Docker, it confines containers to a strict set of capabilities and file access paths, preventing compromised containers from accessing host resources or sensitive data. |
| **Q2** | How do AppArmor profiles help secure a Docker container? | AppArmor profiles define granular rules dictating which files/directories can be read, written, or executed, what network sockets can be opened, and which Linux kernel capabilities the containerized process may utilize. |
| **Q3** | Why is it important to restrict access to sensitive directories such as `/etc/` and `/var/`? | Sensitive directories like `/etc/` contain system configurations, credentials, and password files (`/etc/passwd`, `/etc/shadow`). Directories like `/var/` contain logs and runtime state. Restricting access prevents information disclosure, credential theft, and unauthorized tampering. |
| **Q4** | What other capabilities can you restrict using AppArmor profiles? | You can restrict raw socket creation (`rawip`), administration privileges (`deny capability sys_admin`), mounting filesystems (`mount/umount`), ptrace debugging, and executing arbitrary binary shells. |
| **Q5** | How can you verify if an AppArmor profile is successfully applied to a Docker container? | Inspect the container using the Docker CLI (`docker inspect <id>`) or Docker SDK for Python (`client.api.inspect_container()`) and check `HostConfig.SecurityOpt`, which contains `['apparmor=<profile-name>']`. Inside a Linux container, you can check `/proc/self/attr/current`. |
