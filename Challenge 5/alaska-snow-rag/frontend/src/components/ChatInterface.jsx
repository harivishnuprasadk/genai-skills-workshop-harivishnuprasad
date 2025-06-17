import React, { useState, useEffect, useRef } from 'react';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [apiStatus, setApiStatus] = useState('checking');
    const messagesEndRef = useRef(null);

    // Use environment variable for API URL
    const API_URL = import.meta.env.VITE_API_URL || 'https://alaska-rag-api-697768193921.us-central1.run.app';

    const sampleQuestions = [
        "What are snow removal procedures?",
        "How do I report road hazards?",
        "When do emergency shelters open?",
        "What are winter emergency protocols?"
    ];

    useEffect(() => {
        checkApiStatus();
        createSnowflakes();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const createSnowflakes = () => {
        const snowflakes = ['❄', '❅', '❆'];
        const interval = setInterval(() => {
            const snowflake = document.createElement('div');
            snowflake.className = 'snowflake';
            snowflake.innerHTML = snowflakes[Math.floor(Math.random() * snowflakes.length)];
            snowflake.style.left = Math.random() * window.innerWidth + 'px';
            snowflake.style.animationDuration = Math.random() * 3 + 5 + 's';
            snowflake.style.opacity = Math.random();
            document.body.appendChild(snowflake);
            
            setTimeout(() => snowflake.remove(), 8000);
        }, 3000);

        // Cleanup interval on component unmount
        return () => clearInterval(interval);
    };

    const checkApiStatus = async () => {
        try {
            const response = await fetch(API_URL + '/');
            if (response.ok) {
                setApiStatus('online');
            } else {
                setApiStatus('offline');
            }
        } catch (err) {
            setApiStatus('offline');
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setError('');
        
        // Add user message
        setMessages(prev => [...prev, { 
            type: 'user', 
            content: userMessage,
            timestamp: new Date().toISOString()
        }]);

        setLoading(true);

        try {
            const response = await fetch(API_URL + '/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: userMessage })
            });

            const data = await response.json();

            if (response.ok) {
                setMessages(prev => [...prev, { 
                    type: 'assistant', 
                    content: data.answer,
                    contextFound: data.context_found,
                    validationStatus: data.validation_status,
                    timestamp: new Date().toISOString()
                }]);
            } else {
                throw new Error(data.detail || 'Failed to get response');
            }
        } catch (err) {
            setError('Failed to connect to the service. Please try again.');
            setMessages(prev => [...prev, { 
                type: 'assistant', 
                content: 'Sorry, I encountered an error. Please try again later.',
                error: true,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleSampleClick = (question) => {
        setInput(question);
    };

    return (
        <div className="app-container">
            <div className="header">
                <h1>
                    ❄️ Alaska Emergency Services Assistant
                </h1>
                <p className="subtitle">
                    Get instant answers about snow removal, road conditions, and emergency protocols
                </p>
                <div className="status-badge">
                    <span className="status-dot" style={{
                        background: apiStatus === 'online' ? '#4caf50' : 
                                  apiStatus === 'offline' ? '#f44336' : '#ff9800'
                    }}></span>
                    API Status: {apiStatus === 'online' ? 'Online' : 
                                apiStatus === 'offline' ? 'Offline' : 'Checking...'}
                </div>
            </div>

            <div className="chat-container">
                {error && (
                    <div className="error-banner">
                        ⚠️ {error}
                    </div>
                )}
                
                <div className="messages-container">
                    {messages.length === 0 ? (
                        <div className="welcome-message">
                            <h2>Welcome to Alaska Emergency Services</h2>
                            <p>Ask me anything about winter services, emergency procedures, or road conditions.</p>
                            <div className="sample-questions">
                                {sampleQuestions.map((q, i) => (
                                    <button 
                                        key={i} 
                                        className="sample-chip"
                                        onClick={() => handleSampleClick(q)}
                                    >
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        messages.map((msg, index) => (
                            <div key={index} className={`message ${msg.type}`}>
                                <div className="message-avatar">
                                    {msg.type === 'user' ? 'U' : 'AI'}
                                </div>
                                <div className={`message-content ${msg.error ? 'message-error' : ''}`}>
                                    {msg.content}
                                </div>
                            </div>
                        ))
                    )}
                    
                    {loading && (
                        <div className="message assistant">
                            <div className="message-avatar">AI</div>
                            <div className="message-content">
                                <div className="loading-dots">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                </div>

                <div className="input-container">
                    <form onSubmit={sendMessage} className="input-form">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask about snow removal, emergencies, or road conditions..."
                            className="input-field"
                            disabled={loading || apiStatus === 'offline'}
                        />
                        <button 
                            type="submit" 
                            className="send-button"
                            disabled={loading || !input.trim() || apiStatus === 'offline'}
                        >
                            {loading ? '...' : 'Send →'}
                        </button>
                    </form>
                    
                    {messages.length === 0 && (
                        <div className="sample-questions">
                            <small style={{color: '#666', marginRight: '10px'}}>Try:</small>
                            {sampleQuestions.slice(0, 2).map((q, i) => (
                                <button 
                                    key={i} 
                                    className="sample-chip"
                                    onClick={() => handleSampleClick(q)}
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;