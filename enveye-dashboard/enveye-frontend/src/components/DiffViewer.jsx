// App-level: Modular version of DiffViewer
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API_BASE_URL } from './api';
import DiffTable from "./DiffTable.jsx";
import DiagnosisPanel from "./DiagnosisPanel.jsx";

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
  const diagnosisRef = useRef();

  useEffect(() => {
    if (diagnosisAI && diagnosisRef.current) {
      diagnosisRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [diagnosisAI]);

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

  if (!diffData || Object.keys(diffData).length === 0) {
    return <div className="mt-8 text-center text-gray-500">No differences found!</div>;
  }

  return (
    <div className="min-h-screen p-6 bg-gray-100 text-gray-900">
      <div className="flex justify-center items-center mb-6">
        <h2 className="text-3xl font-bold">🚀 EnvEye - Snapshot Differences</h2>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        <DiffTable diffData={diffData} />

        <DiagnosisPanel
          ref={diagnosisRef}
          diagnosisAI={diagnosisAI}
          sessionId={sessionId}
          chatHistory={chatHistory}
          followupText={followupText}
          setFollowupText={setFollowupText}
          sendFollowup={sendFollowup}
          chatLoading={chatLoading}
          startDiagnosis={startDiagnosis}
          waitingDiagnosis={waitingDiagnosis}
          errorMsg={errorMsg}
          setErrorMsg={setErrorMsg}
          errorScreenshot={errorScreenshot}
          handleFileChange={handleFileChange}
          logPath={logPath}
          setLogPath={setLogPath}
        />
      </div>
    </div>
  );
}

export default DiffViewer;
