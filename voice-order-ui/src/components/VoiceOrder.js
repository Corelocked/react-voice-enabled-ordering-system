import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { signOut } from "firebase/auth";
import { auth } from '../firebase';
import axios from 'axios';
import innsightLogo from '../components/innsight_logo_png.png';

// IMPORTS BY CHRIS
import 'bootstrap/dist/css/bootstrap.min.css';
import './VoiceOrder.css';
import Form from 'react-bootstrap/Form';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const VoiceOrder = () => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState('');
    const [chosenVoice, setChosenVoice] = useState(null);
    const navigate = useNavigate();

    // Load preferred voice for text-to-speech
    useEffect(() => {
        const loadVoices = () => {
            const voices = speechSynthesis.getVoices();
            console.log("Available voices:", voices);
            const selectedVoice = voices.find(voice => voice.name === 'Microsoft Libby Online (Natural) - English (United Kingdom)');
            
            // Voice List:
            // Microsoft Zira - English (United States)
            // Microsoft Mark - English (United States)
            // Microsoft David - English (United States) - Default
            // Microsoft Nanami Online (Natural) - Japanese (Japan)
            // Microsoft SunHI Online (Natural) - Korean (Korea)
            // Microsoft Libby Online (Natural) - English (United Kingdom)

            if (selectedVoice) {
                console.log("Selected voice:", selectedVoice);
                setChosenVoice(selectedVoice);
            } else {
                console.warn("Preferred voice not found, using default voice.");
                setChosenVoice(voices[0]);
            }
        };

        loadVoices();

        speechSynthesis.onvoiceschanged = loadVoices;
    }, []);

    // Start voice recognition
    const startVoiceRecognition = () => {
        if (!SpeechRecognition) {
            alert("Your browser does not support Speech Recognition.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            console.log('Voice recognition started. Speak into the microphone.');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setInput(transcript); // Update input state with recognized speech
            console.log('You said: ', transcript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error: ', event.error);
            setResponse('Error in voice recognition. Please try again.');
        };

        recognition.onend = () => {
            console.log('Voice recognition ended.');
        };

        recognition.start();
    };

    // Handle the voice order submission
    const handleVoiceOrder = async () => {
        if (!input) {
            alert('Please provide a voice input or type a request before submitting.');
            return;
        }

        setLoading(true);
        try {
            // Send order to the backend API
            const res = await axios.post('http://localhost:5000/api/voice-order', { input });

            // Check response from server and update response state
            if (res.data && res.data.response) {
                setResponse(res.data.response);
                speakResponse(res.data.response);
            } else {
                setResponse('Unexpected response format from the server.');
            }

            setInput(''); // Clear input field
        } catch (error) {
            let errorMessage = 'An error occurred. Please try again.';
            if (error.response) {
                errorMessage = error.response.data?.error || error.response.statusText;
            } else if (error.request) {
                errorMessage = 'No response from the server. Please check your network connection.';
            } else {
                errorMessage = error.message;
            }
            setResponse(errorMessage);
        } finally {
            setLoading(false); 
        }
    };

    const speakResponse = (responseText) => {
        const utterance = new SpeechSynthesisUtterance(responseText);
        utterance.voice = chosenVoice;
        utterance.pitch = 1.8; 
        utterance.rate = 1.1; 

        window.speechSynthesis.speak(utterance);
    };

    // Handle feedback submission to backend API
    const handleFeedback = async () => {
        if (!feedback) {
            alert('Please provide your feedback.');
            return;
        }

        try {
            await axios.post('http://localhost:5000/api/feedback', { feedback });
            setFeedback('');
            alert('Thank you for your feedback!');
        } catch (error) {
            alert('Error submitting feedback. Please try again.');
        }
    };

    // Handle user logout and redirect to login page
    const handleLogout = async () => {
        try {
            await signOut(auth); 
            navigate("/login"); 
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    return (
        <div className="order-page">
            <div className="order-container"> 
            <img src={innsightLogo} alt="logo" />
            <p><b>INNSIGHT</b></p>
                <div>
                    <Form.Group className="mb-3" controlId="requestArea">
                        <Form.Label><b>Request:</b></Form.Label>
                        <Form.Control
                            as="textarea"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            rows={4}
                            placeholder="Type your request here..."
                        />
                    </Form.Group>
                    <button onClick={startVoiceRecognition} disabled={loading}>Start Voice Input</button>
                    <button onClick={handleVoiceOrder} disabled={loading || !input}>
                        {loading ? 'Processing...' : 'Submit Order'}
                    </button>
                </div>
                {response && (
                    <div className="response-container">
                        <p><b>Response:</b></p>
                        <p>{response}</p>
                    </div>
                )}
                <div>
                    <Form.Group className="mb-3" controlId="feedbackArea">
                        <Form.Label><b>Feedback:</b></Form.Label>
                        <Form.Control
                            as="textarea"
                            value={feedback}
                            onChange={(e) => setFeedback(e.target.value)}
                            rows={2}
                            placeholder="Provide feedback here..."
                        />
                    </Form.Group>
                    <button onClick={handleFeedback}>Submit Feedback</button>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </div>
        </div>
    );
};

export default VoiceOrder;
