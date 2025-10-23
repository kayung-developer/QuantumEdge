# DortMed - Advanced AI-Powered Medical System

DortMed is a comprehensive, AI-powered, and secure medical platform designed to bridge the gap between patients and healthcare providers. It leverages a modern microservices architecture to deliver a seamless experience, including telemedicine, AI-assisted diagnostics, secure record management, and a global network of healthcare facilities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/dortania/OpenCore-Legacy-Patcher)

## ✨ Core Features

DortMed is a feature-rich platform tailored to the distinct needs of patients, physicians, and administrators.

### For Patients
- **Secure Authentication:** Firebase-powered registration and login with Two-Factor Authentication (2FA).
- **Personalized Dashboard:** A central hub with AI-driven alerts, upcoming appointments, and health snapshots.
- **Medical Records Management:** Securely upload, store, and access all medical documents.
- **AI-Powered OCR:** Automatically extract data from uploaded lab results with our OCR service.
- **Find a Doctor:** Advanced search for physicians by specialty with geospatial search to find doctors nearby.
- **Appointment Booking:** View physician availability and book, reschedule, or cancel appointments in real-time.
- **Telemedicine:** Engage in secure, high-quality video consultations powered by Twilio.
- **AI Wellness Suite:** Receive personalized wellness plans, check for drug interactions, and get daily health tips.
- **Subscription & Billing:** Manage subscriptions and view billing history with secure Paystack integration.

### For Physicians
- **Verification Workflow:** A secure onboarding process with admin verification of credentials.
- **Practice Dashboard:** Get AI-driven analytics on consultation volume, patient satisfaction, and more.
- **Schedule Management:** Easily define and update your availability and working hours.
- **Patient Management:** Access a comprehensive list of your patients and their full medical histories.
- **AI Diagnostic Support:** Leverage a powerful rule-based engine for diagnostic suggestions to aid clinical decisions.
- **E-Prescribing:** Generate and securely save PDF prescriptions directly to a patient's records.
- **Communication Hub:** Engage in secure, real-time chat with patients.
- **Professional Development:** Access a curated list of medical journals, courses, and resources.

### For Administrators
- **Master Dashboard:** A 360-degree view of the platform with KPIs like total users, pending verifications, and Monthly Recurring Revenue (MRR).
- **User Management:** View, search, filter, and manage all users on the platform.
- **Physician Verification Queue:** Approve or reject new physician applications.
- **Feature Flag Management:** Enable or disable features for different subscription tiers in real-time without deploying new code.
- **System Audit Trail:** A comprehensive log of all critical actions performed across the platform for security and compliance.
- **Content Management System (CMS):** Create, update, and manage blog posts for the public-facing Health Hub.

## 🏛️ System Architecture

DortMed is built on a modern, decoupled microservices architecture to ensure scalability, maintainability, and resilience.

- **Core Backend (FastAPI):** The primary API built with Python and FastAPI. It handles business logic, user management, database interactions (via SQLAlchemy), and serves as the main gateway.
- **AI Inference Service (FastAPI):** A dedicated microservice for hosting and serving machine learning models. It loads a pre-trained `scikit-learn` model to provide cardiovascular risk predictions.
- **OCR Service (FastAPI):** A lightweight microservice that uses `pytesseract` to perform Optical Character Recognition on uploaded lab result images, returning structured data.
- **Frontend (React):** A responsive and dynamic Single Page Application (SPA) built with React, utilizing Tailwind CSS for styling and a rich set of libraries like `react-router`, `chart.js`, and `leaflet` for a modern user experience.
- **Background Scheduler:** A standalone Python script using `apscheduler` to handle recurring tasks like sending appointment reminders.
- **Database:** Uses SQLAlchemy ORM, making it compatible with databases like PostgreSQL (for production) and SQLite (for development).
- **External Services:** Integrates with best-in-class third-party services:
  - **Firebase:** For Authentication, Cloud Storage, and Push Notifications (FCM).
  - **Twilio:** For real-time video and communication services.
  - **Paystack:** For secure and reliable payment processing.

## 🛠️ Tech Stack

**Backend & Services:**
- **Language:** Python 3.9+
- **Frameworks:** FastAPI, Pydantic
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL (Production), SQLite (Development)
- **AI/ML:** Scikit-learn, PyTesseract, Pandas
- **Async:** Uvicorn, httpx, asyncio
- **Authentication:** Firebase Admin SDK, python-jose (JWT), bcrypt

**Frontend:**
- **Framework:** React 18
- **Language:** JavaScript (ES6+) with JSX
- **Styling:** Tailwind CSS, PostCSS
- **Routing:** React Router
- **State Management:** React Context API
- **API Communication:** Axios
- **UI/Animation:** Headless UI, Framer Motion
- **Charts & Maps:** Chart.js, Leaflet

**Infrastructure & DevOps:**
- **Cloud Services:** Firebase (Auth, Storage, FCM), Twilio, Paystack
- **Containerization:** Docker / Docker Compose (implied for microservices deployment)

## 🚀 Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing purposes.

### Prerequisites

- **Python** (v3.9 or higher)
- **Node.js** (v16 or higher) with `npm`
- **Tesseract OCR Engine**: You must install Google's Tesseract engine on your local machine.
  - [Installation Guide for Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- Access to **Firebase**, **Twilio**, and **Paystack** accounts to get API keys.

### 1. Configuration

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd dortmed-project
    ```
2.  **Backend Configuration:**
    - Navigate to the `backend` directory.
    - Create a `.env` file by copying `.env.example` (if provided) or creating a new one.
    - Populate the `.env` file with your credentials:
      ```env
      # Application Settings
      SECRET_KEY="your_super_secret_key"
      DATABASE_URL="sqlite:///./dortmed.db" # Or "postgresql://user:pass@host/db"

      # Firebase
      FIREBASE_CREDENTIALS_PATH="path/to/your/firebase-admin-sdk.json"
      FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"

      # Twilio
      TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      TWILIO_AUTH_TOKEN="your_auth_token"
      TWILIO_API_KEY_SID="SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      TWILIO_API_KEY_SECRET="your_api_secret"

      # Paystack
      PAYSTACK_SECRET_KEY="sk_test_xxxxxxxxxxxxxxxxxxxxxx"

      # AI/OCR Services URL (if running locally)
      AI_SERVICE_URL="http://localhost:8080"
      OCR_SERVICE_URL="http://localhost:8090"
      ```

3.  **Frontend Configuration:**
    - In `frontend/src/firebase.js`, replace the placeholder `firebaseConfig` with your actual Firebase project configuration from the Firebase console.
    - In `frontend/public/firebase-messaging-sw.js`, do the same.
    - In `frontend/src/hooks/useFCM.js`, replace `YOUR_VAPID_KEY_FROM_FIREBASE_CONSOLE` with your VAPID key from Firebase Project Settings > Cloud Messaging.

### 2. Installation & Setup

**Backend Services:**

1.  **Set up Virtual Environment:**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create Mock AI Model:**
    The AI service requires a model file. Generate a mock model:
    ```bash
    python ai_service/create_mock_model.py
    ```
4.  **Run the Services:**
    Open three separate terminal windows, activate the virtual environment in each, and run the services:
    ```bash
    # Terminal 1: Core Backend
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

    # Terminal 2: AI Service
    uvicorn ai_service.main:app --host 0.0.0.0 --port 8080 --reload

    # Terminal 3: OCR Service
    uvicorn ocr_service.main:app --host 0.0.0.0 --port 8090 --reload
    ```
    The database and initial feature flags will be created on the first run.

**Frontend Application:**

1.  **Navigate and Install Dependencies:**
    ```bash
    cd frontend
    npm install
    ```
2.  **Run the Development Server:**
    ```bash
    npm start
    ```
    The application should now be running on `http://localhost:3000`.

## 📚 API Documentation

The FastAPI backend provides automatic, interactive API documentation. Once the core backend service is running, you can access it at:

-   **Swagger UI:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
-   **ReDoc:** [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
