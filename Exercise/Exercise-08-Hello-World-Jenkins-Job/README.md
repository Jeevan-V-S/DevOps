# Exercise 8: Creating "Hello World" Jenkins Job

## Objective
Create a Bash script (`hello-world.sh`), push it to GitHub, configure a Jenkins Freestyle Job named `HelloWorld`, and automate its execution via Jenkins.

---

## 1. Script Creation & Git Push
Created `hello-world.sh`:
```bash
#!/bin/bash
echo "Hello, Jenkins!"
```

- Added to repository root and `Exercise-08-Hello-World-Jenkins-Job/`
- Pushed to GitHub repository: **`https://github.com/Jeevan-V-S/DevOps.git`**

---

## 2. Jenkins Setup & Job Configuration

### Prerequisites: Running Jenkins
- Jenkins runs via Docker on `http://localhost:8080`.
- Initial Admin Password:
  ```
  bbb0a530fe8e442489d7f60e65ad31e4
  ```

### Step-by-Step Job Setup

1. **Access Jenkins**:
   - Open `http://localhost:8080` in your web browser.
   - Log in using your credentials / initial admin password.

2. **Create New Item**:
   - Click **"New Item"** in the left menu.
   - Enter name: **`HelloWorld`**
   - Select **"Freestyle project"** and click **OK**.

3. **Configure the Job**:
   - **General**: Add description `Hello World! Jenkins job.`
   - **Source Code Management**:
     - Select **Git**
     - Repository URL: `https://github.com/Jeevan-V-S/DevOps.git`
     - Branch Specifier: `*/main`
   - **Build Steps**:
     - Click **Add build step** ➔ **Execute shell**
     - Shell command:
       ```bash
       sh hello-world.sh
       ```

4. **Run the Job**:
   - Click **Save**.
   - Click **Build Now** in the left sidebar.

---

## 3. Expected Console Output

When the build completes, open **Build History** ➔ **#1** ➔ **Console Output**:

```text
Started by user Admin
Building in workspace /var/jenkins_home/workspace/HelloWorld
Cloning the remote Git repository
Cloning repository https://github.com/Jeevan-V-S/DevOps.git
 > git init /var/jenkins_home/workspace/HelloWorld # timeout=10
Fetching upstream changes from https://github.com/Jeevan-V-S/DevOps.git
 > git --version # timeout=10
 > git fetch --tags --force --progress -- https://github.com/Jeevan-V-S/DevOps.git +refs/heads/*:refs/remotes/origin/* # timeout=10
Checking out Revision 25a6045... (origin/main)
[HelloWorld] $ /bin/sh -xe /tmp/jenkins8921739812.sh
+ sh hello-world.sh
Hello, Jenkins!
Finished: SUCCESS
```

---

## 4. Key Takeaways
- **Freestyle Projects** in Jenkins allow straightforward setup of build tasks without coding complex pipelines.
- **SCM Integration** pulls the exact revision of the script from GitHub.
- **Execute shell** step triggers local script execution inside the container environment.
