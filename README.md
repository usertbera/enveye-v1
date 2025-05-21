
<p align="center">
  <img src="https://github.com/usertbera/enveye-v1/blob/main/enveye-dashboard/enveye-frontend/src/assets/logo_96x96.png" alt="EnvEye Logo" width="120" height="120"/>
</p>

<h1 align="center">EnvEye - Intelligent Snapshot Comparator</h1>

<p align="center">
  💻 Compare. 🤔 Analyze. 🚀 Fix. <br/>
  <em>Debugging environments smarter & faster.</em>
</p>

<p align="center">
  <a href="https://github.com/usertbera/enveye-v1"><img alt="Built With" src="https://img.shields.io/badge/Built%20with-React%20%7C%20FastAPI%20%7C%20AI-blue?style=for-the-badge"/></a>
  <a href="https://github.com/usertbera/enveye-v1/blob/main/LICENSE">
  <a href="https://github.com/usertbera/enveye-v1/blob/main/LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge"/>
  </a>
  <img alt="OCR Enabled" src="https://img.shields.io/badge/OCR%20Support-Tesseract-informational?style=for-the-badge"/>
</p>

---

## 📈 Project Overview

**EnvEye** is a smart debugging assistant for IT environments.  
It compares snapshots of system states (e.g., two VMs) and highlights key differences.  
Powered by popular AI models, it explains issues and suggests fixes instantly.

Built for developers, DevOps, and IT support teams — to accelerate troubleshooting and root cause analysis.

<p align="center">
  <a href="https://youtu.be/xwLIr30wqGQ" target="_blank">
    <img src="https://github.com/user-attachments/assets/e45aeff2-977f-4a53-bd38-d4eaf9690b49" alt="EnvEye Demo Video" width="600" style="border-radius: 8px;"/>
    <br>
    <strong>▶️ Watch Demo Video</strong>
  </a>
</p>

---

## 📸 Screenshots

<p align="center">
  <img src="https://github.com/user-attachments/assets/e45aeff2-977f-4a53-bd38-d4eaf9690b49" alt="Screenshot 1" style="margin: 20px 0; width: 80%; max-width: 800px;"/>
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/035ce254-a1eb-40ea-b1fc-2024a1e3e596" alt="Screenshot 2" style="margin: 20px 0; width: 80%; max-width: 800px;"/>
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/45df4d05-027b-41e2-b868-8c2b0d0ceea3" alt="Screenshot 3" style="margin: 20px 0; width: 80%; max-width: 800px;"/>
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/55c680c9-44a4-478e-a5b3-292165ab66eb" alt="Screenshot 4" style="margin: 20px 0; width: 80%; max-width: 800px;"/>
</p>

---

## 🛠️ EnvEye Architecture Diagram

<p align="center">
  <img src="https://github.com/user-attachments/assets/bbfedc26-3234-4a5a-99fb-fd0a4ee0eeed" alt="EnvEye Architecture Diagram" width="600"/>
</p>

----

## 🏆 Why EnvEye Matters

**EnvEye empowers IT support teams and developers to dramatically reduce Mean Time To Resolution (MTTR)** by automating the discovery of environment-related issues. Instead of manually inspecting configurations, services, DLLs, or logs, teams can rely on EnvEye’s intelligent comparison and AI-powered diagnostics.

### 💡 Real-World Use Case

> A support engineer receives a critical bug report from staging: “It worked yesterday.”  
> Using EnvEye, they instantly compare snapshots from today and yesterday, OCR a provided error screenshot, and get AI-generated insights into the root cause — saving hours of guesswork and back-and-forth debugging.

---

## 🧆 Key Features

- 💾 **Snapshot Collection**: Remote/manual VM snapshot capture.
- 🔍 **DeepDiff Comparison**: Detects changes across OS, DLLs, services, configs.
- 🧠 **AI-Powered Analysis**: Smart diagnosis using popular AI models.
- 🖼️ **Screenshot Debugging**: Upload an error screenshot – OCR extracts the message!
- 📁 **Log Path Support**: Mention a backend-accessible log file path for full AI context.
- 📋 **Clean & Friendly UI**: View, upload, download snapshots effortlessly.
- ✉️ **Error Message Assistance**: Input or upload errors to get pinpointed AI help.

---

## 🚀 Tech Stack

| Layer       | Techs Used                            |
| ----------- | ------------------------------------- |
| Frontend    | React + Vite + TailwindCSS            |
| Backend     | FastAPI (Python)                      |
| AI Model    | OpenAI/Gemini/Perplexity                |
| OCR Engine  | Tesseract OCR (via pytesseract)       |
| Collector   | GO Agent using WinRM/SSH              |
| Diff Engine | DeepDiff (Python)                     |

---

## 🔍 How It Works

1. 📥 **Collect Snapshots**: Capture environment context (services, registry, DLLs, configs).
2. 🔍 **Upload & Compare**: Upload two snapshots to generate a DeepDiff report.
3. 🧾 **Input Error Context** (Optional):
   - Paste an error message
   - Upload a screenshot (auto OCR)
   - Or provide a **log file path** accessible to the backend
4. 🧠 **Request AI Help**: All inputs are sent to AI models for analysis.
5. 🛠️ **Get Solutions**: Receive probable causes and intelligent suggestions.

---

## 🌐 Setup Instructions
Clone the repository https://github.com/usertbera/enveye-v1

### 👉 EnvEye Agent Creation
- Go 1.16 or higher installed

Inside enveye-agent folder run the build_all script

macOS/Linux
```
chmod +x build-all.sh
./build-all.sh
```
Windows (PowerShell)
```
.build-all.ps1
```
Once the script run successfully agents for windows/linux/darwin(mac) will be created in respective folder
```
dist/
├── windows_amd64/enveye-agent.exe
├── linux_amd64/enveye-agent
├── darwin_amd64/enveye-agent
├── darwin_arm64/enveye-agent
```




---

### 👉 EnvEye Dashboard Setup
For Windows:
```
run start_all.bat
```

For Linux/macOS:
```shell
chmod +x start_all.sh
.\start_all.sh
```
**Update config.json file:**
```json
{
  "backend_ip": "http:localhost:8000",
  "agent_paths": {
    "windows": "C:\\dist\\windows_amd64\\enveye-agent.exe",
    "linux": "/home/dist/linux_amd64/enveye-agent",
    "macos": "/Users/yourname/darwin_amd64/enveye-agent"
  },
  "ai": {
    "vendor": "openai",
    "model": "gpt-4"            
  }
}
```

**Environment Variable Required:**
create a .env file in root of the project (enveye-dashboard) and add api keys for the AI model being used
```
  OPENAI_API_KEY //for open ai
  GOOGLE_API_KEY //for google gemini

```
**Optional: Install OCR Dependencies**
```bash
sudo apt install tesseract-ocr         # Linux
brew install tesseract                 # macOS
choco install tesseract                # Windows (via Chocolatey)
```

---

## ⚙️ Setup for Remote Collection

To enable remote snapshot collection:

1. Copy 'dist' folder which was generated during agent creation in remote VM (e.g., `C:\dist\..`), Make sure the path is provided correctly in config.json
   **⚙️ Make the Binary Executable (Linux/macOS)**  
```shell
chmod +x enveye-agent
```
2. On the VM, **run the following script once**:

For Windows:
```
run WinRMFixScript.ps1
```


For Linux/macOS:
```shell
chmod +x SSHFixScript.sh
.\SSHFixScript.sh
```

---

## 📂 Project Structure

```
/enveye-dashboard
  /enveye-frontend     # React frontend (Vite based)
  /enveye-backend      # FastAPI backend
/enveye-agent          # go agent for snapshot collection
```
---
### 🤖➕🧑‍🏫 Feedback-Driven AI (Human-in-the-Loop)

EnvEye isn't just smart — it's learning-friendly.

Every AI explanation can be flagged by the user as inaccurate, making the tool safer and more responsible. This allows for:

- ✅ Human-in-the-loop review of misdiagnoses
- ✅ Transparent debugging and traceability
- ✅ Collection of edge cases for future model improvement

> 🙋‍♂️ **See something wrong? Just flag it.**

---

## ⚡ Limitations

- Large snapshots (>10MB) may slightly slow comparisons.
- AI diagnosis is best-effort — manual validation recommended.
- Log path analysis requires backend to have read access.

---

## 🌈 Future Enhancements

- 🔥 AI-prioritized diff summaries.
- 📦 Batch snapshot comparison support.
- 🪵 Smart log scanning (pattern detection, timestamps, etc.)

---
## 🌩️ Cloud-Native Vision (Roadmap)

As infrastructure continues to evolve toward the cloud, EnvEye is designed to evolve with it. Snapshot-based debugging remains a **critical tool** in modern, distributed systems — and we’re building toward native cloud support.

### 🔭 Planned Cloud Integrations:

| Goal                             | Description |
|----------------------------------|-------------|
| ☁️ **Cloud VM Support**         | Support for snapshot collection from **AWS EC2**, **Azure VMs**, and **GCP Compute Engine** — using native APIs (SSM, Azure RunCommand, etc.) |
| 📦 **Docker & Kubernetes Snapshots** | Capture and compare environment state inside **containers** and **K8s pods** — such as env vars, mounts, and sidecar configs |
| ⚙️ **Cloud Log Integration**     | Fetch relevant logs directly from **CloudWatch**, **Azure Monitor**, or **GCP Logging** when a path or tag is provided |
| 🔁 **GitOps & CI/CD Awareness** | Compare snapshots against known-good state from a GitOps repo or before/after deployment scripts |
| 🧠 **AI Root Cause for Cloud Drift** | Use AI to explain mismatches in multi-region, auto-scaled deployments or ephemeral node pools |

> ✨ Whether it's a Windows VM, a Linux container, or a dynamic microservice — EnvEye will help you debug it faster.

---
## 📅 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for more details.

---

## 🙏 Acknowledgements

- 🧠 OpenAI, Google, Perplexity 
- ⚡ DeepDiff for intelligent diffing
- 🧾 Tesseract OCR
- ❤️ Open-source community inspirations

---

> Made with passion to simplify IT and DevOps life! 🚀
