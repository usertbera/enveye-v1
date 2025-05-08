import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from "./api";

function DiagnosisChat({ initialPayload }) {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]); // {role, content}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const startDiagnosis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/start_diagnosis`, initialPayload);
      setSessionId(response.data.session_id);
      setMessages([
        { role: "user", content: "Start Diagnosis" },
        { role: "assistant", content: response.data.ai_response }
      ]);
    } catch (err) {
      console.error("Failed to start diagnosis", err);
      alert("❌ Failed to start diagnosis.");
    } finally {
      setLoading(false);
    }
  };

  const sendFollowup = async () => {
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/followup`, {
        session_id: sessionId,
        followup_text: userMessage
      });
      setMessages((prev) => [...prev, { role: "assistant", content: response.data.ai_response }]);
    } catch (err) {
      console.error("Followup failed", err);
      alert("❌ AI failed to respond.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-3xl mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">🧠 AI Diagnosis Assistant</h2>

      {!sessionId ? (
        <button
          onClick={startDiagnosis}
          disabled={loading}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          {loading ? "Starting..." : "Start AI Diagnosis"}
        </button>
      ) : (
        <>
          <div
            ref={chatRef}
            className="border rounded p-4 max-h-96 overflow-y-auto bg-gray-50 space-y-4 mb-4"
          >
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg max-w-[80%] whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-blue-100 self-end ml-auto text-right"
                    : "bg-gray-200 self-start"
                }`}
              >
                {msg.content}
              </div>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type your follow-up..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 border px-4 py-2 rounded"
              onKeyDown={(e) => e.key === "Enter" && sendFollowup()}
              disabled={loading}
            />
            <button
              onClick={sendFollowup}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Send
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default DiagnosisChat;
