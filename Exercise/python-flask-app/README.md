# Exercise: Jenkins Multi-Stage Pipeline: Deploying a Python Application

## Objective
Create and execute a Jenkins Pipeline performing multiple stages: **Build**, **Test**, **Deploy**, **Run Application**, and **Test Application** for a Python Flask application.

---

## Directory Structure (`python-flask-app/`)
```
python-flask-app/
├── app.py            # Flask web application exposing "/"
├── requirements.txt  # Project dependencies (flask)
├── test_app.py       # Python unittest validating status code & body
└── Jenkinsfile       # Multi-stage Declarative Pipeline definition
```

---

## 1. Application Code & Tests

### `app.py`
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"

if __name__ == "__main__":
    app.run(debug=True)
```

### `requirements.txt`
```text
flask==2.1.2
```

### `test_app.py`
```python
import unittest
from app import app

class TestApp(unittest.TestCase):
    def test_home(self):
        tester = app.test_client()
        response = tester.get("/")
        print(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), "Hello, Jenkins Multi-Stage Pipeline!")

if __name__ == "__main__":
    unittest.main()
```

---

## 2. Multi-Stage Pipeline Definition (`Jenkinsfile`)

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'python3 -m unittest discover -s .'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                mkdir -p ${WORKSPACE}/python-app-deploy
                cp ${WORKSPACE}/app.py ${WORKSPACE}/python-app-deploy/
                '''
            }
        }
        stage('Run Application') {
            steps {
                echo 'Running application...'
                sh '''
                nohup python3 ${WORKSPACE}/python-app-deploy/app.py > ${WORKSPACE}/python-app-deploy/app.log 2>&1 &
                echo $! > ${WORKSPACE}/python-app-deploy/app.pid
                '''
            }
        }
        stage('Test Application') {
            steps {
                echo 'Testing application...'
                sh '''
                python3 ${WORKSPACE}/test_app.py
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for more details.'
        }
    }
}
```

---

## 3. Resolving Jenkins Docker Missing Dependencies (Step 8)
When running inside standard `jenkins/jenkins:lts`, Python3 and Flask must be installed on the build agent:
```bash
docker exec -it -u root jenkins bash
apt-get update
apt-get install -y python3 python3-pip python3-flask
```
✅ **Installed**: `Python 3.13.5` and `python3-flask 3.1.1` inside container.

---

## 4. Test Stage Execution & Verification
Ran unittests inside the Jenkins container environment:
```bash
python3 -m unittest discover -s . -v
```
**Output:**
```text
test_home (test_app.TestApp.test_home) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
Hello, Jenkins Multi-Stage Pipeline!
```

---

## 5. Pipeline Stages Walkthrough

| Stage | Action | Expected Result | Status |
|---|---|---|---|
| **Build** | Prepares workspace & checks dependencies | `Creating virtual environment...` | ✅ Success |
| **Test** | Executes `python3 -m unittest discover -s .` | `Ran 1 test... OK` | ✅ Success |
| **Deploy** | Creates deployment dir & copies `app.py` | Copied to `${WORKSPACE}/python-app-deploy/` | ✅ Success |
| **Run Application** | Starts Flask via `nohup` in background | Saves PID to `app.pid` | ✅ Success |
| **Test Application** | Re-executes test client against deployed copy | `Hello, Jenkins Multi-Stage Pipeline!` | ✅ Success |
| **Post Actions** | Runs declarative post block | `Pipeline completed successfully!` | ✅ Success |
