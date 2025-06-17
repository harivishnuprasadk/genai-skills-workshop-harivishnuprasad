Alaska Emergency Services Assistant Agent

This project implements a secure, scalable Generative AI assistant for the Alaska Department of Emergency Services. It leverages Retrieval-Augmented Generation (RAG) with Google BigQuery and Gemini AI to provide context-aware, validated answers from departmental knowledge sources. The application is built with Python (FastAPI) and is fully Dockerized for deployment on Google Cloud Run. The frontend is hosted as a static site on the google cloud storage.

Backend Endpoint:
https://alaska-rag-api-697768193921.us-central1.run.app/ask

Frontend Application URL:
https://storage.googleapis.com/alaska-rag-chat-qwiklabs-gcp-02-e6e6123d96ed/index.html

The application has the following features implemented:



1. Backend data store for RAG was loaded using the queries on the BigQuery console.
2. The Backend API uses FastAPI built with python and was dockerized and deployed on the Google Cloud Functions.
3. The unit tests were written using pytest with mock data
4. The evaluation data was done using the Google Evaluation Service API.
5. Prompt filtering was done by passing the user input to the model before passing to the GenAI model.
6. The Backend was consumed in the React frontend application and was deployed as a static site on the google cloud storage.

Folder Structure:
alaska-snow-rag/
├── backend/ # Backend API logic (FastAPI + RAG system)
│ ├── main.py # FastAPI application entry point
│ ├── config.py # Configuration and environment handling
│ ├── rag_system.py # Core RAG retrieval + Gemini generation logic
│ ├── prompt_validator.py # Input safety and validation filters
│ ├── evaluation.py # Response evaluation (local + Google Eval)
│ ├── test_local.py # Local test driver for RAG
│ ├── test_unit.py # Unit tests for individual backend components
│ ├── test_data.py # Sample inputs/expected outputs
│ ├── requirements.txt # Backend dependencies
│ ├── Dockerfile # Docker config for Cloud Run
│ ├── .env.yaml # Env vars for deployment
│ └── .dockerignore # Docker context exclusions
│
├── frontend/ # Vite/React frontend UI
│ ├── index.html # App entry HTML
│ ├── vite.config.js # Vite build config
│ ├── package.json # Frontend dependencies
│ ├── dist/ # Production build (auto-generated)
│ └── src/
│ ├── main.jsx # App entry point
│ ├── App.jsx # Root UI component
│ ├── ChatInterface.jsx # Main chat window
│ └── styles/ # CSS files
│ ├── App.css
│ └── index.css

NOTE: We use the .env and .env.yaml for the credentials

Local Testing:
#run local RAG
python test_local.py

# Run all unit tests

pytest test_unit.py -v

# Run specific test class

pytest test_unit.py::TestRAGSystem -v

# Run with coverage

pytest test_unit.py --cov=. --cov-report=html

# Full evaluation with Google Evaluation Service

python evaluation.py

# Quick local evaluation (without Google service)

python evaluation.py --quick

Steps to Dockerize and Deploy:

# Set project ID

export PROJECT_ID=$(gcloud config get-value project)

# Build and push to Google Container Registry

gcloud builds submit --tag gcr.io/$PROJECT_ID/alaska-rag-api:latest

# Deploy the container to cloud run

gcloud run deploy alaska-rag-api \
 --image gcr.io/$PROJECT_ID/alaska-rag-api:latest \
 --region us-central1 \
 --platform managed \
 --allow-unauthenticated \
 --memory 1Gi \
 --timeout 300 \
 --env-vars-file .env.yaml

Frontend Local Testing:

# Install dependencies

npm install

# Run development server

npm run dev

Production Build:
npm run build

Deploy to Google Cloud Storage:

# Create a bucket for hosting

export BUCKET_NAME="alaska-rag-chat-$RANDOM"
gsutil mb gs://$BUCKET_NAME

# Upload built files

gsutil -m cp -r dist/\* gs://$BUCKET_NAME/

# Make bucket public

gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Enable website configuration

gsutil web set -m index.html -e 404.html gs://$BUCKET_NAME

# Get the public URL

echo "Your app is live at: https://storage.googleapis.com/$BUCKET_NAME/index.html"
