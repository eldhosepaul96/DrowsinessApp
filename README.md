# DrowsinessApp
---

# Real-time Web Drowsiness Detection

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=yellow)![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-05998b?logo=fastapi)![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)![TypeScript](https://img.shields.io/badge/TypeScript-4.9+-3178C6?logo=typescript&logoColor=white)![Socket.IO](https://img.shields.io/badge/Socket.IO-4.5+-010101?logo=socket.io)

A real-time drowsiness detection system that uses a web browser to monitor a user's attention level. The application captures video via webcam, processes it on a Python backend using **MediaPipe**, and provides immediate visual and audible feedback through a React frontend.

**(Optional: Add a GIF of the application in action here)**
`![Demo GIF](link_to_your_demo.gif)`

---

## 📋 Features

-   **🌐 Fully Web-Based**: No desktop installation required. Runs directly in your browser.
-   **🚀 Real-time Processing**: Low-latency video streaming and analysis using WebSockets (Socket.IO).
-   **🧠 Advanced Face Tracking**: Employs Google's MediaPipe Face Mesh for highly accurate and fast facial landmark detection without needing extra model files.
-   **👁️ Eye Aspect Ratio (EAR)**: Precisely calculates eye openness to detect drowsiness and micro-sleeps.
-   **🔊 Visual & Audible Alerts**: The interface changes color and plays distinct sounds for "Drowsy" and "Sleeping" states to alert the user.
-   **💪 Robust & Resilient**: Gracefully handles moments when the user's face is temporarily out of frame.
-   **👥 Multi-Client Ready**: The backend architecture is designed to manage states for multiple concurrent users.

## ⚙️ How It Works

The system operates on a client-server model:

1.  **Frontend (React Client)**
    -   Captures video frames from the user's webcam.
    -   Encodes each frame as a Base64 JPEG image.
    -   Sends the encoded image to the backend via a WebSocket every 100ms.
    -   Listens for status updates from the backend.
    -   Dynamically updates the UI (status text, color) and triggers audio alerts based on the received data.

2.  **Backend (Python Server)**
    -   A FastAPI server manages WebSocket connections using Socket.IO.
    -   Receives the Base64 image, decodes it, and converts it into an OpenCV-compatible format.
    -   Uses the MediaPipe library to detect facial landmarks on the image.
    -   Calculates the Eye Aspect Ratio (EAR) from the eye landmark coordinates.
    -   Analyzes the EAR over several frames to determine the user's state (Active, Drowsy, or Sleeping).
    -   Emits the status back to the correct client.



## 🛠️ Tech Stack

| Component      | Technologies                                                              |
| :------------- | :------------------------------------------------------------------------ |
| **Backend**    | `Python`, `FastAPI`, `Uvicorn`, `python-socketio`, `OpenCV`, `MediaPipe`   |
| **Frontend**   | `React`, `TypeScript`, `socket.io-client`, `CSS`                          |
| **Protocol**   | `WebSockets`                                                              |

## 📁 Project Structure

```
DrowsinessApp/
├── backend/
│   ├── main.py             # FastAPI/Socket.IO server logic
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── public/
│   │   └── sounds/
│   │       ├── drowsy_alert.mp3
│   │       └── sleeping_alert.mp3
│   ├── src/
│   │   ├── App.css         # Component styles
│   │   └── App.tsx         # Main React component
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

## 🚀 Getting Started

### Prerequisites

-   **Python 3.8+** and `pip`
-   **Node.js v14+** and `npm` (or `yarn`)
-   A webcam connected to your computer.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/eldhosepaul96/DrowsinessApp.git
    cd DrowsinessApp
    ```

2.  **Setup the Backend:**
    ```sh
    # Navigate to the backend directory
    cd backend

    # (Recommended) Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Setup the Frontend:**
    ```sh
    # Create React app
    npx create-react-app frontend --template typescript
    
    # Navigate to the frontend directory from the root
    cd ../frontend

    # Install npm packages
    npm install
    ```

### Running the Application

You must run both the backend and frontend servers in separate terminals.

1.  **Start the Backend Server:**
    -   In your terminal for the `backend` directory, run:
    ```sh
    uvicorn main:socket_app --host 0.0.0.0 --port 8000
    ```
    -   The server is now listening on `http://localhost:8000`.

2.  **Start the Frontend Application:**
    -   In a **new terminal** for the `frontend` directory, run:
    ```sh
    npm start
    ```
    -   Your browser should automatically open to `http://localhost:3000`.

## 🕹️ Usage

1.  Open `http://localhost:3000` in your browser.
2.  Click the **"Start Monitoring"** button.
3.  Grant the browser permission to access your webcam.
4.  The application will start displaying your video feed and real-time drowsiness status.

## 🔧 Configuration

You can fine-tune the detection sensitivity by modifying these constants in `backend/main.py`:

-   `NO_FACE_THRESHOLD`: Number of consecutive frames without a face before the status resets.
-   `ACTIVE_THRESHOLD`: The EAR value above which the user is considered "Active."
-   `DROWSY_THRESHOLD`: The EAR value below which the user is considered "Sleeping." The range between this and `ACTIVE_THRESHOLD` is "Drowsy."
