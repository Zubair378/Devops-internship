# DevOps Internship - Week 1

## Project Overview

This project contains two independent Python-based microservices built using the Flask framework, containerized using optimized multi-stage Docker images.

* **Backend Service** (Port 5000)
* **Frontend Service** (Port 5001)

Each service is fully independent — built, run, and verified separately using Docker.


<img width="1920" height="1080" alt="Screenshot (1201)" src="https://github.com/user-attachments/assets/de7edc16-c0c4-4f31-a739-4fd0f33f20a6" />



## Project Structure

```
devops-week1/
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── README.md
```

## Technologies Used

* Python 3.12
* Flask
* Docker (multi-stage builds)
* WSL2 (Ubuntu)
* kubectl, Terraform, Helm (installed and verified as prerequisites)



## Prerequisites Verified

| Tool | Status |
|---|---|
| WSL2 (Ubuntu) | Installed |
| Docker | v29.6.1 |
| kubectl | v1.36.1 |
| Terraform | v1.15.7 |
| Helm | v4.2.3 |


<img width="612" height="248" alt="a" src="https://github.com/user-attachments/assets/fc89a24a-5d1d-41f4-bf0f-bbd6e0e5b827" />



## Microservices

### Backend Service
Runs on port **5000**.

Available endpoints:
* `GET /health`
* `GET /info`

Example:
```
http://localhost:5000/info
```

### Frontend Service
Runs on port **5001**.

Available endpoints:
* `GET /health`
* `GET /info`

Example:
```
http://localhost:5001/info
```

> Note: Frontend and backend currently run as fully independent services. Service-to-service communication (frontend calling backend) is a planned next step, not part of Week 1 scope.

## Docker

Each microservice includes an optimized, multi-stage Dockerfile.

**Features:**
* Multi-stage build (separate builder and runtime stages)
* Lightweight runtime image (`python:3.12-slim`)
* Runs as a non-root user (`appuser`)
* Exposes the required application port

### Build Docker Images

**Backend**
```
cd backend
docker build -t backend:1.0 .
```

**Frontend**
```
cd frontend
docker build -t frontend:1.0 .
```

### Run Docker Containers

**Backend**
```
docker run -d --name backend -p 5000:5000 backend:1.0
```

**Frontend**
```
docker run -d --name frontend -p 5001:5001 frontend:1.0
```

### Verify Running Containers
```
docker ps
```

<!-- Add screenshot of docker ps output here -->


### Verify Endpoints

**Backend Health**
```
curl http://localhost:5000/health
```

**Backend Info**
```
curl http://localhost:5000/info
```

**Frontend Health**
```
curl http://localhost:5001/health
```

**Frontend Info**
```
curl http://localhost:5001/info
```

<!-- Add screenshot of curl outputs here -->


### Verify Non-Root User

Check the user inside each running container.

<img width="1438" height="261" alt="image" src="https://github.com/user-attachments/assets/4ff18aaf-4b23-4671-9163-6b3ee294da70" />


**Backend**
```
docker exec -it backend whoami
```

**Frontend**
```
docker exec -it frontend whoami
```

Expected output:
```
appuser
```

## Outcome

* Verified all required prerequisites (WSL2, Docker, kubectl, Terraform, Helm).
* Developed two independent Python/Flask microservices.
* Implemented `/health` and `/info` endpoints on both services.
* Wrote optimized, multi-stage Dockerfiles for both services.
* Configured both containers to run as a non-root user (`appuser`).
* Built and tagged Docker images locally.
* Verified successful container execution using `docker run`.
* Verified endpoints using `curl`.
* Verified non-root user execution using `docker exec`.
