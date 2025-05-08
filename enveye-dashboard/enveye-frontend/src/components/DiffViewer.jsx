import { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from './api';

function DiffViewer({ diffData }) {
  const [errorMsg, setErrorMsg] = useState("");
  const [errorScreenshot, setScreenshot] = useState(null);
  const [logPath, setLogPath] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [diagnosisAI, setDiagnosisAI] = useState("");
  const [waitingDiagnosis, setWaitingDiagnosis] = useState(false);
  const [followupText, setFollowupText] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    if (diagnosisAI) {
      document.getElementById("ai-diagnosis")?.scrollIntoView({ behavior: "smooth" });
    }
  }, [diagnosisAI]);

  if (!diffData || Object.keys(diffData).length === 0) {
    return <div className="mt-8 text-center text-gray-500">No differences found!</div>;
  }

  const prettifyPath = (path) =>
    path.replace("root", "").replace(/\['/g, " > ").replace(/'\]/g, "").replace(/^ > /, "").trim();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith("image/")) {
      if (file.size > 5 * 1024 * 1024) {
        alert("File too large. Please upload an image smaller than 5MB.");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => setScreenshot(reader.result);
      reader.readAsDataURL(file);
    } else {
      alert("Please upload a valid image file.");
    }
  };

  const extractTextFromImage = async (base64Image) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ocr`, {
        base64_image: base64Image,
      });
      return response.data.text || "";
    } catch (err) {
      console.warn("OCR failed:", err);
      return "";
    }
  };

  const readLogContents = async (logPath) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/read_log`, { path: logPath });
      return response.data.content || "";
    } catch (err) {
      console.warn("Failed to read log:", err);
      return "";
    }
  };

  const startDiagnosis = async () => {
    try {
      setWaitingDiagnosis(true);

      const payload = {
        diff: diffData,
        error_message: errorMsg,
        error_screenshot_text: errorScreenshot ? await extractTextFromImage(errorScreenshot) : "",
        log_content: logPath ? await readLogContents(logPath) : ""
      };

      const response = await axios.post(`${API_BASE_URL}/start_diagnosis`, payload);
      setSessionId(response.data.session_id);
      setDiagnosisAI(response.data.ai_response);

      setChatHistory([{ role: "ai", content: response.data.ai_response }]);
    } catch (err) {
      console.error("Diagnosis failed", err);
      alert("\u274C Failed to start diagnosis.");
    } finally {
      setWaitingDiagnosis(false);
    }
  };

  const sendFollowup = async () => {
    if (!followupText.trim()) return;
    setChatLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/followup`, {
        session_id: sessionId,
        followup_text: followupText
      });
      setChatHistory(prev => [
        ...prev,
        { role: "user", content: followupText },
        { role: "ai", content: response.data.ai_response }
      ]);
      setFollowupText("");
    } catch (err) {
      alert("❌ Follow-up failed.");
      console.error(err);
    } finally {
      setChatLoading(false);
    }
  };

  function renderChangeRow(type, path, oldValue, newValue, index) {
    let bgColor = "bg-green-100";
    if (type === "Removed") bgColor = "bg-red-100";
    else if (type === "Changed") bgColor = "bg-yellow-100";

    const renderCell = (value) => {
      if (value === null || value === undefined) return "-";
      if (typeof value === "object") {
        return <pre className="whitespace-pre-wrap break-words text-xs max-w-xs">{JSON.stringify(value, null, 2)}</pre>;
      }
      return value.toString();
    };

    return (
      <tr key={`${type}-${path}-${index}`} className="border-b">
        <td className={`px-4 py-2 font-semibold text-sm w-32 whitespace-nowrap ${bgColor}`}>{type}</td>
        <td className={`px-4 py-2 text-sm max-w-xs truncate whitespace-nowrap ${bgColor}`}>{prettifyPath(path)}</td>
        <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{renderCell(oldValue)}</td>
        <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{renderCell(newValue)}</td>
      </tr>
    );
  }

  const parsedRows = [];
  if (diffData.values_changed) {
    Object.entries(diffData.values_changed).forEach(([path, change], index) =>
      parsedRows.push(renderChangeRow("Changed", path, change.old_value, change.new_value, index)));
  }
  if (diffData.dictionary_item_added) {
    Object.entries(diffData.dictionary_item_added).forEach(([path, value], index) =>
      parsedRows.push(renderChangeRow("Added", path, "-", value, index)));
  }
  if (diffData.dictionary_item_removed) {
    Object.entries(diffData.dictionary_item_removed).forEach(([path, value], index) =>
      parsedRows.push(renderChangeRow("Removed", path, value, "-", index)));
  }

  return (
    <div className="min-h-screen p-6 bg-gray-100 text-gray-900">
      <div className="flex justify-center items-center mb-6">
        <h2 className="text-3xl font-bold">🚀 EnvEye - Snapshot Differences</h2>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        <div className="flex-1 bg-white rounded-lg shadow-lg p-4 overflow-auto max-h-[80vh]">
          <h3 className="text-2xl font-semibold mb-4">🔍 Differences</h3>
          <div className="overflow-x-auto max-h-[70vh] overflow-y-auto border rounded-lg shadow">
            <table className="min-w-full bg-white">
              <thead className="sticky top-0 bg-gray-200">
                <tr className="text-gray-700">
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Path</th>
                  <th className="px-4 py-2 text-left">Old Value</th>
                  <th className="px-4 py-2 text-left">New Value</th>
                </tr>
              </thead>
              <tbody>{parsedRows}</tbody>
            </table>
          </div>
        </div>

        <div className="flex-1 bg-white rounded-lg shadow-lg p-4 flex flex-col gap-4">
          <h3 className="text-xl font-semibold">🧠 Start AI Diagnosis</h3>
          <textarea
            placeholder="Optional: Error message"
            className="w-full px-4 py-2 border rounded"
            value={errorMsg}
            onChange={(e) => setErrorMsg(e.target.value)}
          />

          <input
            type="text"
            placeholder="Optional: Enter log file path"
            className="w-full px-4 py-2 border rounded text-sm"
            value={logPath}
            onChange={(e) => setLogPath(e.target.value)}
          />

          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="text-sm"
          />

          <button
            onClick={startDiagnosis}
            disabled={waitingDiagnosis}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mt-2"
          >
            {waitingDiagnosis ? "🔍 Starting..." : "Start AI Diagnosis"}
          </button>

          {diagnosisAI && (
            <div id="ai-diagnosis" className="bg-green-100 text-gray-900 p-4 mt-4 rounded shadow">
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
      </div>
    </div>
  );
}

export default DiffViewer;
