import React, { useState } from 'react';
import axios from 'axios';

// Check for browser compatibility
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const VoiceOrder = () => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    // Function to start voice recognition
    const startVoiceRecognition = () => {
        if (!SpeechRecognition) {
            alert("Your browser does not support Speech Recognition.");
            return;
        }

        const recognition = new SpeechRecognition(); // Create a new SpeechRecognition object
        recognition.continuous = false; // Stop automatically after one result
        recognition.interimResults = false; // Do not show interim results

        // Set up the event handlers
        recognition.onstart = () => {
            console.log('Voice recognition started. Speak into the microphone.');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript; // Get the recognized speech
            setInput(transcript); // Set the input state to the recognized speech
            console.log('You said: ', transcript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error: ', event.error);
            setResponse('Error in voice recognition. Please try again.');
        };

        recognition.onend = () => {
            console.log('Voice recognition ended.');
        };

        recognition.start(); // Start voice recognition
    };

    const handleVoiceOrder = async () => {
        if (!input) {
            alert('Please provide a voice input or type a request before submitting.');
            return;
        }
        
        setLoading(true);
        try {
            console.log("Sending input to API:", input); // Log input before sending
            const res = await axios.post('http://localhost:5000/api/voice-order', {
                input: input
            });
            
            // Log the entire response to see its structure
            console.log("API Response:", res); 
            console.log("API Response Data:", res.data); // Log just the data part

            // Check for response data and set it accordingly
            if (res.data && res.data.response) {
                setResponse(res.data.response); // Assuming the response structure contains { response: ... }
            } else {
                setResponse('Unexpected response format from the server.');
            }
            
            // Clear the input box after submission
            setInput(''); // Reset input state
        } catch (error) {
            // Improved error handling
            let errorMessage = 'An error occurred. Please try again.';
            if (error.response) {
                errorMessage = error.response.data?.error || error.response.statusText;
            } else if (error.request) {
                errorMessage = 'No response from the server. Please check your network connection.';
            } else {
                errorMessage = error.message;
            }
            setResponse(errorMessage); // Set the response to the error message
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h1>Voice Activated Order System</h1>
            <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                rows="4"
                cols="50"
                placeholder="Type your request here..."
                style={{ marginBottom: '10px', width: '100%' }}
            />
            <div>
                <button onClick={startVoiceRecognition} disabled={loading} style={{ margin: '5px' }}>
                    Start Voice Input
                </button>
                <button onClick={handleVoiceOrder} disabled={loading || !input} style={{ margin: '5px' }}>
                    {loading ? 'Processing...' : 'Submit Order'}
                </button>
            </div>
            {response && (
                <div style={{ marginTop: '20px' }}>
                    <h3>Response:</h3>
                    <p style={{ padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}>
                        {response}
                    </p>
                </div>
            )}
        </div>
    );
};

export default VoiceOrder;
