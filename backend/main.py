import cv2
import numpy as np
import mediapipe as mp
import base64
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Constants ---
# How many consecutive frames without a face before we reset the status.
# This prevents flickering when the model momentarily loses the face.
NO_FACE_THRESHOLD = 10 

# --- Initialize MediaPipe Face Mesh ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --- Drowsiness Detection Logic ---
def compute_distance(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

def calculate_ear(landmarks):
    left_p1, left_p4 = landmarks[362], landmarks[263]
    left_p2, left_p6 = landmarks[385], landmarks[380]
    left_p3, left_p5 = landmarks[387], landmarks[373]
    left_ear = (compute_distance(left_p2, left_p6) + compute_distance(left_p3, left_p5)) / (2.0 * compute_distance(left_p1, left_p4))

    right_p1, right_p4 = landmarks[33], landmarks[133]
    right_p2, right_p6 = landmarks[160], landmarks[144]
    right_p3, right_p5 = landmarks[158], landmarks[153]
    right_ear = (compute_distance(right_p2, right_p6) + compute_distance(right_p3, right_p5)) / (2.0 * compute_distance(right_p1, right_p4))
    
    return (left_ear + right_ear) / 2.0

# --- FastAPI and Socket.IO Setup ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
socket_app = socketio.ASGIApp(sio, app)

# --- State Management ---
# Store state for each connected client to handle multiple users
CLIENT_STATES = {}

def get_initial_state():
    """Returns a dictionary with the initial state for a new client."""
    return {
        'sleep': 0, 'drowsy': 0, 'active': 0,
        'no_face_counter': 0,
        'status': 'Initializing...',
        'color': '#FFFFFF'
    }

@sio.on('connect')
async def connect(sid, environ):
    print(f"New client connected: {sid}")
    CLIENT_STATES[sid] = get_initial_state()

@sio.on('image')
async def receive_image(sid, data):
    """Process image data received from the client."""
    if sid not in CLIENT_STATES:
        return # Guard against messages from disconnected clients

    state = CLIENT_STATES[sid]

    try:
        header, encoded = data.split(",", 1)
        img_data = base64.b64decode(encoded)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        
        ear = 0.0

        if results.multi_face_landmarks:
            # Face found: reset no_face_counter and process landmarks
            state['no_face_counter'] = 0
            
            for face_landmarks in results.multi_face_landmarks:
                landmarks = np.array([(lm.x * frame.shape[1], lm.y * frame.shape[0]) for lm in face_landmarks.landmark])
                ear = calculate_ear(landmarks)

                ACTIVE_THRESHOLD = 0.25
                DROWSY_THRESHOLD = 0.21

                if ear < DROWSY_THRESHOLD:
                    state['sleep'] += 1; state['drowsy'] = 0; state['active'] = 0
                    if state['sleep'] > 6:
                        state['status'] = "SLEEPING !!!"; state['color'] = "#FF0000"
                elif DROWSY_THRESHOLD <= ear < ACTIVE_THRESHOLD:
                    state['drowsy'] += 1; state['sleep'] = 0; state['active'] = 0
                    if state['drowsy'] > 6:
                        state['status'] = "Drowsy !"; state['color'] = "#FFFF00"
                else:
                    state['active'] += 1; state['sleep'] = 0; state['drowsy'] = 0
                    if state['active'] > 6:
                        state['status'] = "Active"; state['color'] = "#00FF00"
        else:
            # No face found: increment counter
            state['no_face_counter'] += 1
            
            # If counter exceeds threshold, reset to a clean state
            if state['no_face_counter'] > NO_FACE_THRESHOLD:
                state.update(get_initial_state()) # Reset all counters
                state['status'] = 'No Face Detected'
        
        # Emit the current state, which will persist even if a face is briefly lost
        await sio.emit('response', {
            'status': state['status'], 
            'color': state['color'], 
            'ear': round(ear, 3)
        }, to=sid)

    except Exception as e:
        print(f"Error processing image for SID {sid}: {e}")

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    if sid in CLIENT_STATES:
        del CLIENT_STATES[sid]

@app.get("/")
def read_root():
    return {"Hello": "World"}
