import './App.css';
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [file, setFile] = useState(null);
  const [youtubeURL, setYoutubeURL] = useState("");
  const [mode, setMode] = useState("text");
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    try {
      setLoading(true);

      if (mode === "text") {
        const res = await axios.post("http://localhost:5000/summarize/text", {
          text: text
        });
        setSummary(res.data.summary);
      }

      if (mode === "pdf") {
        const formData = new FormData();
        formData.append("file", file);

        const res = await axios.post(
          "http://localhost:5000/summarize/pdf",
          formData
        );
        setSummary(res.data.summary);
      }

      if (mode === "youtube") {
        const res = await axios.post("http://localhost:5000/summarize/youtube", {
          url: youtubeURL
        });
        setSummary(res.data.summary);
      }

    } catch (error) {
      alert("Error occurred.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>🧠 AI Summarizer System</h1>

      <div className="mode-selection">
        <button onClick={() => setMode("text")} className={mode==="text"?"active":""}>Text</button>
        <button onClick={() => setMode("pdf")} className={mode==="pdf"?"active":""}>PDF</button>
        <button onClick={() => setMode("youtube")} className={mode==="youtube"?"active":""}>YouTube</button>
      </div>

      {mode === "text" && (
        <textarea value={text} onChange={(e)=>setText(e.target.value)} placeholder="Enter text..." />
      )}

      {mode === "pdf" && (
        <input type="file" accept="application/pdf" onChange={(e)=>setFile(e.target.files[0])}/>
      )}

      {mode === "youtube" && (
        <input type="text" value={youtubeURL} onChange={(e)=>setYoutubeURL(e.target.value)} placeholder="Enter YouTube URL"/>
      )}

      <button className="main-btn" onClick={handleSummarize}>
        {loading ? "Summarizing..." : "Summarize"}
      </button>

      {summary && (
        <div className="summary">
          <h2>Summary</h2>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default App;
