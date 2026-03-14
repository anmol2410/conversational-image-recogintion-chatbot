/**
 * Speech-to-text button: start/stop recording, set transcript to parent.
 * Uses Web Speech API (SpeechRecognition).
 */
import { useState, useRef } from "react";

export default function VoiceInputButton({ onTranscript, disabled }) {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      onTranscript?.("[Speech not supported in this browser]");
      return;
    }
    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-US";
    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      onTranscript?.(text);
    };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setListening(false);
  };

  return (
    <button
      type="button"
      className={`voice-input-btn ${listening ? "listening" : ""}`}
      onClick={listening ? stopListening : startListening}
      disabled={disabled}
      title={listening ? "Stop listening" : "Voice input"}
      aria-label={listening ? "Stop listening" : "Start voice input"}
    >
      {listening ? "⏹" : "🎤"}
    </button>
  );
}
