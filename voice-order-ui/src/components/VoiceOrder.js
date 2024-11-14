import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

const VoiceOrder = () => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState('');
    const [chosenVoice, setChosenVoice] = useState(null);

    useEffect(() => {
        // Define a function to load voices and select the preferred voice
        const loadVoices = () => {
            const voices = speechSynthesis.getVoices();
            console.log("Available voices:", voices);

            const selectedVoice = voices.find(voice => voice.name === 'Microsoft Libby Online (Natural) - English (United Kingdom)');
            
            //Voice List: 
            //Microsoft Zira - English (United States)
            //Microsoft Mark - English (United States)
            //Microsoft David - English (United States) - Default
            //Microsoft Nanami Online (Natural) - Japanese (Japan)
            //Microsoft SunHI Online (Natural) - Korean (Korea)


            if (selectedVoice) {
                console.log("Selected voice:", selectedVoice);
                setChosenVoice(selectedVoice);
            } else {
                console.warn("Google UK English Female voice not found, using default voice.");
                setChosenVoice(voices[0]);
            }
        };

        loadVoices();

        speechSynthesis.onvoiceschanged = loadVoices;
    }, []);

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
            const res = await axios.post('http://localhost:5000/api/voice-order', { input });

            if (res.data && res.data.response) {
                setResponse(res.data.response);
                speakResponse(res.data.response);
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

        utterance.pitch = 1.8;
        utterance.rate = 1.1;
        utterance.voice = chosenVoice;

        window.speechSynthesis.speak(utterance);
    };

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

    return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
            <h1>Voice Activated Order System</h1>
            <>
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
            </>
        </div>
    );
};

export default VoiceOrder;
