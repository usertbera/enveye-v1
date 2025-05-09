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
    <div className="flex-1 bg-white rounded-lg shadow-lg p-6 flex flex-col gap-6">
      <h3 className="text-xl font-semibold">🧠 Start AI Diagnosis</h3>

      {/* Error Message & Screenshot Upload */}
      <div>
        <label htmlFor="error-message" className="block text-sm font-medium text-gray-700 mb-1">
          Optional Error Message
        </label>
        <textarea
          id="error-message"
          placeholder="Paste a relevant error message..."
          className="w-full px-4 py-2 border rounded focus:outline-none focus:ring"
          value={errorMsg}
          onChange={(e) => setErrorMsg(e.target.value)}
        />

        <div className="flex items-center mt-2 gap-2">
          <label
            htmlFor="screenshot-upload"
            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded cursor-pointer text-sm"
            title="Upload Screenshot"
          >
            Upload Screenshot
          </label>
          <input
            id="screenshot-upload"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          {errorScreenshot && (
            <span className="text-xs text-green-600">✅ Screenshot uploaded</span>
          )}
        </div>

        {errorScreenshot && (
          <div className="mt-3">
            <img src={errorScreenshot} alt="Screenshot preview" className="max-h-48 rounded shadow" />
          </div>
        )}
      </div>

      {/* Log File Path */}
      <div>
        <label htmlFor="log-path" className="block text-sm font-medium text-gray-700 mb-1">
          Optional Log File Path
        </label>
        <input
          id="log-path"
          type="text"
          placeholder="Enter log file path"
          className="w-full px-4 py-2 border rounded text-sm focus:outline-none focus:ring"
          value={logPath}
          onChange={(e) => setLogPath(e.target.value)}
        />
      </div>

      {/* Start Diagnosis Button */}
      <button
        onClick={startDiagnosis}
        disabled={waitingDiagnosis}
        className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
      >
        {waitingDiagnosis ? "🔍 Starting..." : "Start AI Diagnosis"}
      </button>

      {/* Diagnosis Result and Chat */}
      {diagnosisAI && (
        <div ref={ref} id="ai-diagnosis" className="bg-green-100 text-gray-900 p-4 rounded shadow mt-4">
          <h3 className="text-lg font-semibold mb-2">🧠 AI Diagnosis</h3>
          <p className="whitespace-pre-line mb-4">{diagnosisAI}</p>

          {/* Follow-up Chat */}
          <div className="border-t pt-4">
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
                className="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring"
              />
              <button
                onClick={sendFollowup}
                disabled={chatLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
              >
                {chatLoading ? "Sending..." : "Send"}
              </button>
            </div>

            {/* Session Actions */}
            <div className="flex justify-between mt-4 text-sm">
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
                className="text-green-700 underline hover:text-green-900"
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
                className="text-red-600 underline hover:text-red-800"
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
