import React, { useState } from "react";
import "./App.css";

const genres = [
  "Fantasy",
  "Sci-Fi",
  "Romance",
  "Mystery",
  "Horror",
  "Adventure",
  "Literary Fiction",
  "Comedy",
];

const tones = [
  "Serious",
  "Humorous",
  "Dark",
  "Uplifting",
  "Mysterious",
  "Dramatic",
];

const lengths = ["Short", "Medium", "Long"];

function App() {
  const [prompt, setPrompt] = useState("");
  const [genre, setGenre] = useState(genres[0]);
  const [tone, setTone] = useState(tones[0]);
  const [length, setLength] = useState(lengths[0]);
  const [apiKey, setApiKey] = useState("");
  const [story, setStory] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setStory("");
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, genre, tone, length, apiKey }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Error generating story.");
      } else {
        setStory(data.story);
      }
    } catch (err) {
      setError("Network error.");
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>📚 AI Story Generator</h1>
      <form className="story-form" onSubmit={handleSubmit}>
        <label>
          OpenAI API Key:
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            required
            placeholder="sk-..."
          />
        </label>
        <label>
          Prompt:
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            required
            placeholder="A robot discovers emotions and falls in love with a human..."
          />
        </label>
        <label>
          Genre:
          <select value={genre} onChange={(e) => setGenre(e.target.value)}>
            {genres.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </label>
        <label>
          Tone:
          <select value={tone} onChange={(e) => setTone(e.target.value)}>
            {tones.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label>
          Length:
          <select value={length} onChange={(e) => setLength(e.target.value)}>
            {lengths.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Story"}
        </button>
      </form>
      {error && <div className="error">❌ {error}</div>}
      {story && (
        <div className="story-container">
          <h2>Your Generated Story</h2>
          <pre>{story}</pre>
        </div>
      )}
      <footer>
        <p>Made with ❤️ using React & Flask</p>
      </footer>
    </div>
  );
}

export default App;
