// DiagnosisPanel.js
import React, { forwardRef } from "react";
import axios from "axios";
import { API_BASE_URL } from "./api";

const DiagnosisPanel = forwardRef(({
  diagnosisAI,
  sessionId,
  chatHistory,
  followupText,
  setFollowupText,
  sendFollowup,
  chatLoading,
  startDiagnosis,
  waitingDiagnosis,
  errorMsg,
  setErrorMsg,
  errorScreenshot,
  handleFileChange,
  logPath,
  setLogPath
}, ref) => {
  return (
    <div className="flex-1 bg-white rounded-lg shadow-lg p-4 flex flex-col gap-4">
      <h3 className="text-xl font-semibold">🧠 Start AI Diagnosis</h3>

      <textarea
        placeholder="Optional: Error message"
        className="w-full px-4 py-2 border rounded"
        value={errorMsg}
        onChange={(e) => setErrorMsg(e.target.value)}
      />

      <label
        htmlFor="screenshot-upload"
        className="bg-purple-600 text-white px-2 py-1 rounded cursor-pointer text-lg"
        title="Upload Screenshot"
      >
        + Upload Screenshot
      </label>
      <input
        id="screenshot-upload"
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
      />
      {errorScreenshot && (
        <>
          <p className="text-xs text-gray-500 mt-1">✅ Screenshot uploaded</p>
          <div className="mb-4">
            <img src={errorScreenshot} alt="Screenshot preview" className="max-h-48 rounded shadow" />
          </div>
        </>
      )}

      <input
        type="text"
        placeholder="Optional: Enter log file path"
        className="w-full px-4 py-2 border rounded text-sm"
        value={logPath}
        onChange={(e) => setLogPath(e.target.value)}
      />

      <button
        onClick={startDiagnosis}
        disabled={waitingDiagnosis}
        className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mt-2"
      >
        {waitingDiagnosis ? "🔍 Starting..." : "Start AI Diagnosis"}
      </button>

      {diagnosisAI && (
        <div ref={ref} id="ai-diagnosis" className="bg-green-100 text-gray-900 p-4 mt-4 rounded shadow">
          <h3 className="text-lg font-semibold mb-2">🧠 AI Diagnosis</h3>
          <p className="whitespace-pre-line mb-4">{diagnosisAI}</p>

          <div className="mt-4 border-t pt-4">
            <h4 className="text-md font-bold mb-2">💬 Continue AI Chat</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto mb-4 p-2 bg-gray-50 rounded border">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`text-sm ${msg.role === 'user' ? 'text-blue-800' : 'text-green-800'}`}>
                  <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={followupText}
                onChange={(e) => setFollowupText(e.target.value)}
                placeholder="Ask a follow-up..."
                className="flex-1 px-4 py-2 border rounded"
              />
              <button
                onClick={sendFollowup}
                disabled={chatLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded"
              >
                {chatLoading ? "Sending..." : "Send"}
              </button>
            </div>

            <div className="flex justify-between mt-4">
              <button
                onClick={async () => {
                  try {
                    await axios.post(`${API_BASE_URL}/session/${sessionId}/close`);
                    alert("✅ Session marked as resolved.");
                  } catch (err) {
                    alert("Failed to mark session resolved.");
                    console.error(err);
                  }
                }}
                className="text-sm text-green-700 underline hover:text-green-900"
              >
                ✅ Mark as Resolved
              </button>

              <button
                onClick={async () => {
                  try {
                    await axios.post(`${API_BASE_URL}/flag`, {
                      session_id: sessionId,
                      reason: "Inaccurate diagnosis or irrelevant suggestions"
                    });
                    alert("⚠️ Feedback submitted. Thank you!");
                  } catch (err) {
                    alert("Failed to submit feedback.");
                    console.error(err);
                  }
                }}
                className="text-sm text-red-600 underline hover:text-red-800"
              >
                ⚠️ Flag as Inaccurate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

export default DiagnosisPanel;
