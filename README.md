# Full-Stack ToDo Application

## Description
This is a full-stack ToDo application designed to demonstrate modern web development practices. It features a robust backend built with FastAPI and a dynamic frontend powered by Next.js. Users can manage their tasks efficiently, providing a seamless and intuitive experience.

## Technologies Used

### Frontend
*   **Next.js:** A React framework for building server-side rendered and static web applications.
*   **React:** A JavaScript library for building user interfaces.
*   **Tailwind CSS:** A utility-first CSS framework for rapidly building custom designs.
*   **Axios:** Promise-based HTTP client for the browser and Node.js.
*   **Zod:** TypeScript-first schema declaration and validation library.

### Backend
*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **Uvicorn:** An ASGI server for FastAPI, providing asynchronous capabilities.
*   **SQLModel:** A library for interacting with SQL databases from Python code, with Python objects. It's designed to be simple, intuitive, and robust, and is based on Pydantic and SQLAlchemy.
*   **PostgreSQL:** A powerful, open-source object-relational database system.
*   **python-dotenv:** For managing environment variables.
*   **python-jose:** For JSON Web Token (JWT) handling.
*   **passlib:** For password hashing.

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### Prerequisites (Local Development)

Before you begin, ensure you have the following installed:

*   **Node.js** (LTS version recommended)
*   **npm** (comes with Node.js)
*   **Python 3.9+**
*   **pip** (comes with Python)
*   **PostgreSQL** database server running

### 1. Clone the Repository

```bash
git clone <repository_url>
cd hack-phase-3 # or your project root directory
```

### 2. Backend Setup

Navigate to the `backend` directory, set up a virtual environment, install dependencies, and configure your environment variables.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables for Backend:**

Create a `.env` file in the `backend` directory with the following content:

```env
DATABASE_URL="postgresql://user:password@host:port/database_name"
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
*   Replace `user`, `password`, `host`, `port`, and `database_name` with your PostgreSQL database credentials.
*   Generate a strong `SECRET_KEY` for JWT.

### 3. Frontend Setup

Navigate to the `frontend` directory, install dependencies, and configure your environment variables.

```bash
cd ../frontend
npm install
```

**Environment Variables for Frontend:**

Create a `.env.local` file in the `frontend` directory with the following content:

```env
NEXT_PUBLIC_API_URL="http://localhost:8000" # Or wherever your backend is running
```
*   Ensure `NEXT_PUBLIC_API_URL` points to your running backend API.

## How to Run the Application (Local Development)

Once both the backend and frontend are set up, you can start them independently.

### 1. Start the Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend will be accessible at `http://localhost:8000`.

### 2. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```
The frontend application will be accessible at `http://localhost:3000` (or another port if 3000 is occupied).

Open your web browser and navigate to `http://localhost:3000` to access the ToDo application.

## Kubernetes Deployment (Minikube)

This section guides you through deploying the ToDo application to a local Kubernetes cluster using Minikube and Helm.

### Prerequisites (Kubernetes Deployment)

Before you begin, ensure you have the following installed:

*   **Minikube:** A tool that runs a single-node Kubernetes cluster locally.
*   **Helm:** The package manager for Kubernetes.

### 1. Start Minikube

Ensure your Minikube cluster is running:
```bash
minikube start
```

### 2. Build Docker Images

Navigate to the `backend` and `frontend` directories and build their respective Docker images. Make sure to use the tags `todo-backend:latest` and `todo-frontend:latest` as these are configured in the Helm chart.

**Build Backend Image:**
```bash
cd backend
docker build -t todo-backend:latest .
cd ..
```

**Build Frontend Image:**
```bash
cd frontend
docker build -t todo-frontend:latest .
cd ..
```

### 3. Load Images into Minikube

Load the built Docker images into the Minikube Docker daemon so they are accessible by the cluster:

```bash
minikube image load todo-frontend:latest todo-backend:latest
```

### 4. Deploy with Helm

Navigate to the `todoflow-chatbot` directory (where your `Chart.yaml` and `values.yaml` are located) and install or upgrade the Helm chart.

**Initial Installation:**
```bash
helm install todoflow-chatbot ./todoflow-chatbot
```

**Upgrade Existing Deployment (after changes to chart or images):**
```bash
helm upgrade todoflow-chatbot ./todoflow-chatbot
```

### 5. Check Deployment Status

Verify that the Kubernetes pods and services are running:

**Check Pods:**
```bash
kubectl get pods
```
You should see `todoflow-chatbot-frontend-...` and `todoflow-chatbot-backend-...` pods in a `Running` status.

**Check Services:**
```bash
kubectl get services
```
You should see `todoflow-chatbot-frontend` and `todoflow-chatbot-backend` services.

**Check Ingress:**
```bash
kubectl get ingress
```
You should see an ingress resource named `todoflow-chatbot` with host `todoflow.local`.

### 6. Access the Application

To access your application, you need to configure your local machine to resolve `todoflow.local` to the IP address of your Minikube instance.

1.  **Get Minikube IP:**
    ```bash
    minikube ip
    ```
2.  **Edit your hosts file:**
    Add an entry like this to your hosts file (e.g., `/etc/hosts` on Linux/macOS, `C:\Windows\System32\drivers\etc\hosts` on Windows):
    ```
    <minikube-ip> todoflow.local
    ```
    Replace `<minikube-ip>` with the actual IP address you get from `minikube ip`.

After updating your hosts file, you should be able to access your frontend application by navigating to `http://todoflow.local` in your web browser. The backend API will be available at `http://todoflow.local/api`.

## Project Structure Overview

```
hack-phase-3/
├── backend/                  # FastAPI backend application
│   ├── src/                  # Backend source code
│   │   ├── api/              # API routes and middleware
│   │   ├── database/         # Database connection and tables
│   │   ├── models/           # SQLModel models
│   │   └── services/         # Business logic and services
│   ├── requirements.txt      # Python dependencies
│   └── ...
├── frontend/                 # Next.js frontend application
│   ├── src/                  # Frontend source code
│   │   ├── components/       # Reusable UI components
│   │   ├── hooks/            # React hooks
│   │   ├── pages/            # Next.js pages (routes)
│   │   ├── services/         # API interaction services
│   │   └── styles/           # Global styles
│   ├── package.json          # Node.js dependencies
│   └── ...
├── todoflow-chatbot/         # Helm chart for Kubernetes deployment
│   ├── Chart.yaml            # Defines the chart
│   ├── values.yaml           # Default values for the chart
│   └── templates/            # Kubernetes resource templates
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
├── README.md                 # Project documentation
└── ...
```

## Testing

### Backend Testing

Navigate to the `backend` directory and run pytest:
```bash
cd backend
source venv/bin/activate # On Windows: .\venv\Scripts\activate
pytest
```

### Frontend Testing

Frontend tests are typically run with a command like:
```bash
cd frontend
npm test
```