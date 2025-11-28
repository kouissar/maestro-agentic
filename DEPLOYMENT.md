# Deployment Guide

This guide explains how to deploy the Gemini 3 Agent System to a Kubernetes cluster.

## Prerequisites

- Docker installed
- Kubernetes cluster (local like Minikube/Kind/Docker Desktop, or remote like GKE/EKS)
- `kubectl` configured

## 1. Build Docker Images

You need to build images for both the backend and the frontend.

### Backend

Run from the root of the project:

```bash
docker build -t gemini3-backend:latest .
```

### Frontend

Run from the `web_ui` directory:

```bash
cd web_ui
docker build -t gemini3-frontend:latest .
cd ..
```

## 2. Push Images (Optional)

If you are using a remote cluster, you need to tag and push these images to a container registry (like Docker Hub or GCR).

```bash
# Example for Docker Hub
docker tag gemini3-backend:latest yourusername/gemini3-backend:latest
docker push yourusername/gemini3-backend:latest

docker tag gemini3-frontend:latest yourusername/gemini3-frontend:latest
docker push yourusername/gemini3-frontend:latest
```

_Note: If you do this, update the `image` fields in `k8s/backend.yaml` and `k8s/frontend.yaml` to match your registry URLs._

If you are using a local cluster (like Minikube), you might need to load the images directly:

```bash
# Minikube example
minikube image load gemini3-backend:latest
minikube image load gemini3-frontend:latest
```

## 3. Configure Secrets

The backend requires `GOOGLE_API_KEY`. Create a Kubernetes secret for it:

```bash
kubectl create secret generic gemini-secrets --from-literal=GOOGLE_API_KEY=your_actual_api_key_here
```

## 4. Deploy to Kubernetes

Apply the manifests:

```bash
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

## 5. Access the Application

Check the status of your pods and services:

```bash
kubectl get pods
kubectl get services
```

If you are using `LoadBalancer` type for the frontend service (default in `k8s/frontend.yaml`):

- On cloud providers, you will get an `EXTERNAL-IP`.
- On local clusters (like Minikube), you might need to run `minikube tunnel` or use `kubectl port-forward`.

To port-forward manually:

```bash
kubectl port-forward service/frontend-service 8080:80
```

Then access the app at `http://localhost:8080`.
