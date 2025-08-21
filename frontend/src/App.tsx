import React, { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import './App.css';

const App: React.FC = () => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const socketRef = useRef<Socket | null>(null);
    
    // State for the application
    const [isSessionActive, setIsSessionActive] = useState<boolean>(false);
    const [status, setStatus] = useState<string>('Not Started');
    const [statusColor, setStatusColor] = useState<string>('#FFFFFF');
    const [ear, setEar] = useState<number>(0);
    
    // NEW: State to hold the camera stream
    const [stream, setStream] = useState<MediaStream | null>(null);
    
    // Refs for our audio elements
    const drowsyAudioRef = useRef<HTMLAudioElement | null>(null);
    const sleepingAudioRef = useRef<HTMLAudioElement | null>(null);
    
    // A ref to track the previous status, initialized to null.
    const prevStatusRef = useRef<string | null>(null);

    // This effect handles playing sounds when the status changes.
    useEffect(() => {
        const drowsyAudio = drowsyAudioRef.current;
        const sleepingAudio = sleepingAudioRef.current;
        const previousStatus = prevStatusRef.current;

        if (!drowsyAudio || !sleepingAudio) return;

        const isNowDrowsy = status.includes('Drowsy') && previousStatus !== status;
        const isNowSleeping = status.includes('SLEEPING') && previousStatus !== status;

        if (isNowDrowsy) {
            sleepingAudio.pause();
            drowsyAudio.play().catch(e => console.error("Drowsy audio play failed:", e));
        } else if (isNowSleeping) {
            drowsyAudio.pause();
            sleepingAudio.play().catch(e => console.error("Sleeping audio play failed:", e));
        } else if (!status.includes('Drowsy') && !status.includes('SLEEPING')) {
            drowsyAudio.pause();
            sleepingAudio.pause();
        }
        
        prevStatusRef.current = status;
    }, [status]);

    // NEW: This effect safely attaches the stream to the video element
    useEffect(() => {
        if (videoRef.current && stream) {
            console.log("Attaching stream to video element.");
            videoRef.current.srcObject = stream;
        }
    }, [stream]); // Runs whenever the `stream` state changes

    const startMonitoring = async () => {
        console.log("Start monitoring clicked.");
        // Initialize Audio
        drowsyAudioRef.current = new Audio('/sounds/drowsy_alert.mp3');
        sleepingAudioRef.current = new Audio('/sounds/sleeping_alert.mp3');
        sleepingAudioRef.current.loop = true;

        // Initialize WebSocket
        socketRef.current = io('http://localhost:8000');
        const socket = socketRef.current;
        socket.on('connect', () => console.log('Connected to backend.'));
        socket.on('disconnect', () => console.log('Disconnected from backend.'));
        socket.on('response', (data: { status: string; color: string; ear: number }) => {
            setStatus(data.status);
            setStatusColor(data.color);
            setEar(data.ear);
        });
        
        // --- Access Webcam ---
        try {
            console.log("Requesting webcam access...");
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
            console.log("Webcam access granted.");
            setStream(mediaStream); // Store the stream in state
            setIsSessionActive(true); // Now we can safely activate the session
        } catch (err) {
            console.error("Error accessing webcam: ", err);
            setStatus("Webcam access denied");
            return;
        }
        
        // --- Start sending frames ---
        const frameInterval = setInterval(() => {
            if (videoRef.current && videoRef.current.srcObject && socket.connected) {
                const canvas = document.createElement('canvas');
                canvas.width = videoRef.current.videoWidth;
                canvas.height = videoRef.current.videoHeight;
                const context = canvas.getContext('2d');
                if (context) {
                    context.translate(canvas.width, 0);
                    context.scale(-1, 1);
                    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
                    const data = canvas.toDataURL('image/jpeg', 0.8);
                    socket.emit('image', data);
                }
            } else {
                clearInterval(frameInterval);
            }
        }, 100);
    };

    return (
        <div className="App">
            <h1>Real-time Drowsiness Detection</h1>

            {isSessionActive ? (
                <>
                    <div className="video-container">
                        {/* The video element now just waits for the stream from the useEffect */}
                        <video ref={videoRef} width="640" height="480" autoPlay muted playsInline />
                    </div>
                    <div className="status-display">
                        <p className="status-text" style={{ color: statusColor }}>
                            {status}
                        </p>
                        <p className="ear-text">
                            Eye Aspect Ratio: {ear.toFixed(3)}
                        </p>
                    </div>
                </>
            ) : (
                <div className="start-container">
                    <p>Click the button to start monitoring.</p>
                    <button onClick={startMonitoring} className="start-button">
                        Start Monitoring
                    </button>
                </div>
            )}
        </div>
    );
};

export default App;
