/* global webkitSpeechRecognition SpeechRecognition */

import React, { useState, useEffect } from "react";

function App() {
  const [recognition, setRecognition] = useState(null);
  const [listening, setListening] = useState(false);
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    if ("webkitSpeechRecognition" in window) {
      const webkitRecognizer = new webkitSpeechRecognition();
      webkitRecognizer.continuous = false;
      webkitRecognizer.interimResults = false;
      webkitRecognizer.lang = "en-US";

      webkitRecognizer.onstart = () => {
        setStatus("Listening...");
        setListening(true);
      };

      webkitRecognizer.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setStatus(`You said: ${transcript}`);
        sendMessage(transcript);
      };

      webkitRecognizer.onerror = (event) => {
        setStatus(`Error occurred: ${event.error}`);
      };

      webkitRecognizer.onend = () => {
        setListening(false);
        setStatus("");
      };

      setRecognition(webkitRecognizer);
    } else if ("SpeechRecognition" in window) {
      const speechRecognizer = new SpeechRecognition();
      speechRecognizer.continuous = false;
      speechRecognizer.interimResults = false;
      speechRecognizer.lang = "en-US";

      speechRecognizer.onstart = () => {
        setStatus("Listening...");
        setListening(true);
      };

      speechRecognizer.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setStatus(`You said: ${transcript}`);
        sendMessage(transcript);
      };

      speechRecognizer.onerror = (event) => {
        setStatus(`Error occurred: ${event.error}`);
      };

      speechRecognizer.onend = () => {
        setListening(false);
        setStatus("");
      };

      setRecognition(speechRecognizer);
    } else {
      alert("Your browser does not support speech recognition.");
    }
  }, []);

  const startListening = () => {
    if (recognition) {
      recognition.start();
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
    }
  };

  const sendMessage = async (message) => {
    setMessage("");
    setChatHistory((prev) => [
      ...prev,
      { user: message, bot: "Processing..." },
    ]);
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      if (data.response) {
        setChatHistory((prev) =>
          prev.map((entry, idx) =>
            idx === prev.length - 1
              ? { ...entry, bot: data.response }
              : entry
          )
        );
      } else {
        setChatHistory((prev) =>
          prev.map((entry, idx) =>
            idx === prev.length - 1
              ? { ...entry, bot: "No response from chatbot." }
              : entry
          )
        );
      }
    } catch (error) {
      setChatHistory((prev) =>
        prev.map((entry, idx) =>
          idx === prev.length - 1
            ? { ...entry, bot: `Error: ${error.message}` }
            : entry
        )
      );
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      sendMessage(message.trim());
    }
  };

  return (
    <div className="App">
      <h1>Chat with the Bot</h1>
      <div id="chat-history" style={{ border: "1px solid #ccc", padding: "10px", height: "300px", overflowY: "scroll", marginBottom: "10px" }}>
        {chatHistory.map((entry, index) => (
          <div key={index}>
            <p><strong>You:</strong> {entry.user}</p>
            <p><strong>Bot:</strong> {entry.bot}</p>
          </div>
        ))}
      </div>
      <div>
        <button id="start-record-btn" onClick={startListening} disabled={listening}>Start Recording</button>
        <button id="stop-record-btn" onClick={stopListening} disabled={!listening}>Stop Recording</button>
        <p id="status">{status}</p>
      </div>
      <form id="chat-form" onSubmit={handleFormSubmit}>
        <input
          type="text"
          id="chat-input"
          placeholder="Enter your message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ flex: 1, padding: "10px", fontSize: "16px" }}
        />
        <button type="submit" style={{ padding: "10px", fontSize: "16px" }}>Send</button>
      </form>
    </div>
  );
}

export default App;
