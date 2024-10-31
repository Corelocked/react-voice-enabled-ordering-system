import React, { useState } from 'react';
import axios from 'axios';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const VoiceOrder = () => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState('');  // Feedback state

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
            setInput(transcript);
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

    const handleVoiceOrder = async () => {
        if (!input) {
            alert('Please provide a voice input or type a request before submitting.');
            return;
        }

        setLoading(true);
        try {
            console.log("Sending input to API:", input);
            const res = await axios.post('http://localhost:5000/api/voice-order', {
                input: input
            });

            console.log("API Response:", res);
            console.log("API Response Data:", res.data);

            if (res.data && res.data.response) {
                setResponse(res.data.response);
                speakResponse(res.data.response);  // Speak the response
            } else {
                setResponse('Unexpected response format from the server.');
            }

            setInput('');
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

    const speakResponse = (response) => {
        const utterance = new SpeechSynthesisUtterance(response);
        window.speechSynthesis.speak(utterance);
    };

    const handleFeedback = async () => {
        if (!feedback) {
            alert('Please provide your feedback.');
            return;
        }

        try {
            await axios.post('http://localhost:5000/api/feedback', { feedback });
            setFeedback('');  // Clear feedback input after submission
            alert('Thank you for your feedback!');
        } catch (error) {
            alert('Error submitting feedback. Please try again.');
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
            <div style={{ marginTop: '20px' }}>
                <h3>Feedback:</h3>
                <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    rows="3"
                    cols="50"
                    placeholder="Provide your feedback here..."
                    style={{ marginBottom: '10px', width: '100%' }}
                />
                <button onClick={handleFeedback} style={{ margin: '5px' }}>
                    Submit Feedback
                </button>
            </div>
        </div>
    );
};

export default VoiceOrder;
