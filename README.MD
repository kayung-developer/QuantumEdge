# QuantumEdge Trader

[![Version](https://img.shields.io/badge/Version-3.0.0-blue.svg)](https://github.com/your-username/quantedge-trader)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-cyan.svg)](https://reactjs.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/your-username/quantedge-trader)

**QuantumEdge Trader** is a sophisticated, 100% real-system automated trading platform designed to interface with the MetaTrader 5 (MT5) terminal. It combines a powerful Python backend with a modern React frontend and a standalone native Windows desktop application, offering a complete suite of tools for strategy backtesting, optimization, and live automated trading.

The system is architected for robustness, scalability, and professional-grade performance, utilizing advanced strategies, including AI/ML models and Smart Money Concepts.

![QuantumEdge Terminal Screenshot](https://i.imgur.com/your-screenshot-url.png)  <!-- Replace with a URL to a screenshot of your app -->

---

## 🚀 Features

The QuantumEdge Trader platform is composed of two main components: a Web Application and a native Windows Desktop Application.

### Core System Features (Shared)
*   **Advanced Strategy Engine:** A modular engine supporting a diverse catalog of nine high-quality trading strategies.
*   **Professional Risk Management:** All trades are executed with dynamic, percentage-based lot sizing and ATR-based stop losses.
*   **Direct MT5 Integration:** Communicates seamlessly with the MT5 terminal for market data and trade execution without relying on fragile third-party bridges.
*   **Multi-Language Support:** Full internationalization for a global user base.
*   **Modern Theming:** Light and Dark mode support for user comfort.

###  Web Application
*   **Cloud-Native Backend:** A robust FastAPI backend designed for deployment on modern cloud platforms like Hugging Face Spaces or Azure.
*   **Reactive Frontend:** A sleek, responsive user interface built with React and Tailwind CSS.
*   **Subscription & Payments:** A complete, secure payment system with multiple providers (PayPal, Paystack, Crypto) and subscription plan gating for premium features.
*   **Superuser Admin Panel:** A comprehensive dashboard for administrators to manage users, subscriptions, and payments.
*   **Real-time Updates:** Utilizes WebSockets for live updates on account status and trade executions.

### Windows Desktop Application (QuantumEdge Terminal)
*   **Native Performance:** A high-performance standalone application built with Python and PyQt6 for a native Windows look and feel.
*   **All-in-One Interface:** Combines connection management, strategy configuration, live position monitoring, and backtesting in a single, professional terminal window.
*   **Thread-Safe Operation:** All background tasks (MT5 connection, trade loop, backtesting) run in separate threads, ensuring the UI is always responsive.
*   **Live Market Charting:** Features a fully equipped, interactive chart with switchable timeframes and symbols.
*   **Standalone Executable:** Can be compiled into a single `.exe` file for easy distribution and installation.

---

## 🛠️ Technology Stack

| Category              | Technology                                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Backend**           | Python 3.10+, FastAPI, Uvicorn, SQLAlchemy (Async), PostgreSQL, SQLite                                        |
| **Frontend (Web)**    | React 18, React Router, Tailwind CSS, Axios, Recharts, Framer Motion, i18next                               |
| **Desktop App**       | Python 3.10+, PyQt6, PyQtGraph                                                                              |
| **Authentication**    | Firebase Authentication (Email/Password, Google)                                                            |
| **AI / Machine Learning** | LightGBM, Scikit-learn, ONNX Runtime, Pandas-TA                                                             |
| **Deployment**        | Docker, Docker Compose, Nginx, Hugging Face Spaces / Microsoft Azure                                        |
| **CI/CD**             | GitHub Actions                                                                                              |

---

## 💰 Acquiring the QuantumEdge Terminal (.EXE)

The **QuantumEdge Terminal** is a premium, standalone Windows application that provides the full suite of trading, backtesting, and analysis tools in a high-performance native package.

### Purchase Information
*   **Program:** QuantumEdge Terminal Executable (`.exe`)
*   **Price:** **$299 USD** (One-time purchase)
*   **License:** Lifetime license for use on a single machine.

### How to Purchase
Due to the custom nature of the software, we handle all purchases directly to ensure proper setup and support.

1.  **Send a Purchase Request:**
    *   Compose an email to: **aondoverslogantechllc@outlook.com**
    *   Use the subject line: `Purchase Request - QuantumEdge Terminal`
    *   In the body of the email, please state your request to purchase the application.

2.  **Payment and Audit:**
    *   You will receive a reply with detailed payment instructions (e.g., via a secure payment link or bank transfer).
    *   After your payment is completed, it will undergo a brief audit for verification.

3.  **Receive the Program:**
    *   Once the payment is confirmed, the complete `QuantumEdgeTerminal.exe` program, along with a setup guide and your license key, will be mailed directly to your desired email address.

---

## 🖥️ Setup and Installation (For Developers)

This section is for developers who wish to run the project from the source code.

### 1. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Configure your .env file with all necessary secrets (DB, Firebase, MT5, etc.)

# Run the server
uvicorn main:app --port 8000 --reload
```

### 2. Frontend (Web App) Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install all dependencies
npm install

# Configure your .env file with Firebase and backend API URL
# REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Run the development server
npm start
```

### 3. Desktop Application Setup
```bash
# Navigate to the desktop_app directory
cd desktop_app

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Run the application
python main.py

# To build the .exe (requires PyInstaller)
python build.py
```

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
