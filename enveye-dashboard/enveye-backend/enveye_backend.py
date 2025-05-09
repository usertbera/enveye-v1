from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from deepdiff import DeepDiff
import google.generativeai as genai
import winrm
import json
import os
import concurrent.futures
import traceback
from pathlib import Path
from datetime import datetime
import base64
from fastapi import Body
from PIL import Image
import pytesseract
import base64
import io
import re
import unicodedata
from ai_provider import send_prompt
from tiktoken import get_encoding
from uuid import uuid4
import paramiko
import time
from config_loader import CONFIG
import sys
sys.path.append(str(Path(__file__).resolve().parent))



# --- FastAPI Application ---
app = FastAPI(title="EnvEye - Context Comparator API")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configure Gemini API ---
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Serve Frontend Static Files ---
app.mount("/static", StaticFiles(directory="../enveye-frontend/dist"), name="static")

# --- Setup Snapshot Directory ---
BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_DIR = BASE_DIR / "snapshots"
SNAPSHOT_DIR.mkdir(exist_ok=True)

# --- Mount Snapshots as Static ---
app.mount("/snapshots", StaticFiles(directory=SNAPSHOT_DIR), name="snapshots")


@app.get("/")
async def serve_spa():
    return FileResponse("../enveye-frontend/dist/index.html")
    
@app.get("/snapshots")
async def serve_spa():
    return FileResponse("../enveye-frontend/dist/index.html")
    
    
@app.get("/config.json")
async def get_config():
    try:
        with open("config.json") as f:
            return JSONResponse(content=json.load(f))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- Upload Snapshot API ---
@app.post("/upload_snapshot")
async def upload_snapshot(request: Request, snapshot: UploadFile = File(...)):
    try:
        form_data = await request.form()
        hostname = form_data.get("hostname", "unknown_host")
        app_folder = form_data.get("app_path", "unknown_app")
        app_name = os.path.basename(app_folder)
        app_name = app_name.replace(" ","")
        
        print(f"app name:{app_name}")

        content = await snapshot.read()
        parsed_content = json.loads(content)

        filename = SNAPSHOT_DIR / f"{hostname}_{app_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        with open(filename, "w") as f:
            f.write(json.dumps(parsed_content, indent=4))

        print(f"\u2705 Snapshot received and saved: {filename}")

        return {"message": f"Snapshot from {hostname} collected successfully!"}

    except Exception as e:
        print(f"\u274C Error while saving snapshot: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# --- Compare Snapshots API ---
@app.post("/compare")
async def compare_snapshots(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        file1_content = await file1.read()
        file2_content = await file2.read()

        data1 = json.loads(file1_content)
        data2 = json.loads(file2_content)

        diff = DeepDiff(data1.get('environment_context', {}), data2.get('environment_context', {}), view='tree')

        return JSONResponse(content={"differences": json.loads(diff.to_json())})

    except Exception as e:
        print(f"\u274C Exception during /compare: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

# --- Explain Differences API (Depreciated) ---
@app.post("/explain")
async def explain_diff(payload: dict = Body(...)):
    try:
        diff = payload.get("diff", {})
        error_message = payload.get("error_message", "").strip()
        error_screenshot = payload.get("error_screenshot", None)
        log_path = payload.get("log_path", "").strip()

        # Extract log content
        log_content = ""
        if log_path:
            full_log = read_log_file_safely(log_path)
            log_content = extract_important_log_blocks(full_log, max_blocks=30)
            
            if estimate_token_count(log_content) > 10000:
                log_content = log_content[:2000] + "\n\n[Log truncated due to size]"

        # Extract text from image if present
        screenshot_text = ""
        if error_screenshot:
            screenshot_text = extract_text_from_screenshot(error_screenshot)

        # Construct the prompt
        prompt = f"""
You are a helpful assistant specialized in IT system configuration comparisons.
Given the following DeepDiff output between two VMs, do the following:

1. Give a summary of what has changed
2. If an error message is provided or found in a screenshot, analyze it in context of the diff.
3. Incorporate log file clues if available.
4. Suggest possible root causes or solutions
5. Be concise and highlight important issues

Diff data:
{json.dumps(diff, indent=2)}

Error message (if any):
{error_message or 'None'}

Error message (from screenshot):
{screenshot_text or 'None'}

Log Content (if any):
{log_content or 'None'}
"""

        # Use OpenAI GPT-4. If "gpt-4.1" is not supported, fallback to "gpt-4"
        response = client.chat.completions.create(
            model="gpt-4",  # Adjust this if "gpt-4.1" is confirmed supported
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        # Aggregate streamed content
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        return {"explanation": full_response}

    except Exception as e:
        print("❌ Error during AI explanation:", e)
        return {"error": str(e)}


#--- AI Diagnosis ---
# --- Diagnosis Session Management ---
sessions = {}

class DiagnosisSession:
    def __init__(self, initial_input):
        self.session_id = str(uuid4())
        self.created_at = datetime.utcnow().isoformat()
        self.initial_input = initial_input
        self.ai_messages = []
        self.user_followups = []
        self.status = "active"

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "initial_input": self.initial_input,
            "ai_messages": self.ai_messages,
            "user_followups": self.user_followups,
            "status": self.status
        }

@app.post("/start_diagnosis")
async def start_diagnosis(payload: dict = Body(...)):
    session = DiagnosisSession(payload)

    prompt = generate_initial_prompt(payload)
    response_text = send_prompt(prompt)

    session.ai_messages.append({"role": "assistant", "content": response_text})
    sessions[session.session_id] = session

    return {
        "session_id": session.session_id,
        "ai_response": response_text
    }

@app.post("/followup")
async def followup(payload: dict = Body(...)):
    session_id = payload.get("session_id")
    followup_text = payload.get("followup_text")

    session = sessions.get(session_id)
    if not session:
        return JSONResponse(content={"error": "Invalid session"}, status_code=404)

    session.user_followups.append({"type": "text", "content": followup_text})
    full_prompt = compile_session_prompt(session)
    ai_response = send_prompt(full_prompt)
    session.ai_messages.append({"role": "assistant", "content": ai_response})

    return {"session_id": session_id, "ai_response": ai_response}

@app.get("/session/{session_id}")
async def view_session(session_id: str):
    session = sessions.get(session_id)
    if not session:
        return JSONResponse(content={"error": "Not found"}, status_code=404)
    return session.to_dict()

@app.post("/session/{session_id}/close")
async def close_session(session_id: str):
    session = sessions.get(session_id)
    if session:
        session.status = "resolved"
    return {"message": f"Session {session_id} marked as resolved"}
    
@app.post("/followup")
async def followup(payload: dict = Body(...)):
    session_id = payload.get("session_id")
    followup_text = payload.get("followup_text")

    session = sessions.get(session_id)
    if not session:
        return JSONResponse(content={"error": "Invalid session"}, status_code=404)

    session.user_followups.append({
        "type": "text",
        "content": followup_text
    })

    # Compile a conversation prompt from history
    full_prompt = compile_session_prompt(session)
    ai_response = send_prompt(full_prompt)

    session.ai_messages.append({"role": "assistant", "content": ai_response})
    return {
        "session_id": session_id,
        "ai_response": ai_response
    }


@app.post("/flag")
async def flag_feedback(payload: dict = Body(...)):
    try:
        session_id = payload.get("session_id")
        reason = payload.get("reason", "No reason provided")

        feedback_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "reason": reason
        }

        with open("flagged_feedback.jsonl", "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        return {"message": "Feedback recorded"}
    except Exception as e:
        print("Feedback error:", e)
        return {"error": str(e)}


# --- Remote Collection API ---
@app.post("/remote_collect")
async def remote_collect(request: Request):
    try:
        body = await request.json()
        vm_ip = body.get("vm_ip")
        username = body.get("username")
        password = body.get("password")
        app_folder = body.get("app_folder")
        app_type = body.get("app_type")
        vm_type = body.get("vm_type", "windows").lower()
        snapshot_label = body.get("label", "").strip()

        hostname = vm_ip.replace('.', '-')
        app_name = os.path.basename(app_folder).replace(" ", "").replace(".", "_")
        timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
        snapshot_filename = f"{hostname}_{app_name}_{vm_type.upper()}_{timestamp}_{snapshot_label}.json"

        if vm_type == "windows":
            return await handle_windows(vm_ip, username, password, app_folder, app_type, snapshot_label, snapshot_filename)
        elif vm_type in ["linux", "macos", "mac"]:
            return await handle_ssh_based(vm_ip, username, password, app_folder, app_type, snapshot_label, snapshot_filename)
        else:
            return JSONResponse(content={"error": f"Unsupported VM type: {vm_type}"}, status_code=400)

    except Exception:
        print("❌ FULL EXCEPTION in /remote_collect")
        print(traceback.format_exc())
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
        
        
        
# for remote colection in Windows VM
async def handle_windows(vm_ip, username, password, app_folder, app_type, snapshot_label, snapshot_filename):
    remote_agent = CONFIG["agent_paths"]["windows"]
    snapshot_dir = os.path.dirname(remote_agent)
    remote_snapshot_path = f"{snapshot_dir}\\{snapshot_filename}"

    try:
        session = winrm.Session(
            f'http://{vm_ip}:5985/wsman',
            auth=(username, password),
            transport='ntlm'
        )

        arg_parts = [
            f'--app-folder "{app_folder}"',
            f'--app-type {app_type}',
            f'--output {snapshot_filename}'
        ]
        if snapshot_label:
            arg_parts.append(f'--label {snapshot_label}')
        arg_string = " ".join(arg_parts)

        ps_cmd = f"""
        Start-Process -FilePath '{remote_agent}' -ArgumentList '{arg_string}' -Wait -NoNewWindow
        """

        print("🚀 Executing agent remotely on Windows...")
        print("🧪 PowerShell Command:\n", ps_cmd)

        exec_result = session.run_ps(ps_cmd)
        print("✅ Remote agent launched.")
        print("STDOUT:", exec_result.std_out.decode())
        print("STDERR:", exec_result.std_err.decode())

        # Wait for snapshot file to appear
        for _ in range(30):
            check_cmd = f"Test-Path '{remote_snapshot_path}'"
            poll_result = session.run_ps(check_cmd)
            if "True" in poll_result.std_out.decode():
                print("📁 Snapshot file detected.")
                break
            time.sleep(1)
        else:
            return JSONResponse(content={"error": "Snapshot file not found after waiting."}, status_code=500)

        # Read and base64-encode the snapshot file
        read_cmd = f"$b = Get-Content -Path '{remote_snapshot_path}' -Raw; [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($b))"
        read_result = session.run_ps(read_cmd)
        encoded_data = read_result.std_out.decode().strip()

        if not encoded_data or "Exception" in encoded_data:
            return JSONResponse(content={"error": "Failed to retrieve snapshot file content."}, status_code=500)

        # Decode and save to local file
        decoded_bytes = base64.b64decode(encoded_data)
        local_file_path = SNAPSHOT_DIR / snapshot_filename
        with open(local_file_path, "wb") as f:
            f.write(decoded_bytes)

        print(f"✅ Snapshot pulled and saved to: {local_file_path}")
        return {
            "status": "success",
            "message": f"Snapshot from {vm_ip} collected and uploaded!",
            "vm_hostname": vm_ip
        }

    except Exception as e:
        print("❌ FULL EXCEPTION in handle_windows")
        print(traceback.format_exc())
        return JSONResponse(content={"error": str(e)}, status_code=500)


        
# for remote collection Linux and Mac VMs        
async def handle_ssh_based(vm_ip, username, password, app_folder, app_type, snapshot_label, snapshot_filename):
    remote_agent_path = CONFIG["agent_paths"]["linux"]
    snapshot_dir = os.path.dirname(remote_agent_path)
    remote_snapshot_path = f"{snapshot_dir}/{snapshot_filename}"

    arg_parts = [
        f'--app-folder "{app_folder}"',
        f'--app-type {app_type}',
        f'--output {remote_snapshot_path}'
    ]
    if snapshot_label:
        arg_parts.append(f'--label {snapshot_label}')
    arg_string = " ".join(arg_parts)

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(vm_ip, username=username, password=password, look_for_keys=False)

        # Ensure output directory exists
        client.exec_command(f"mkdir -p {snapshot_dir}")

        # Run agent
        full_command = f"{remote_agent_path} {arg_string}"
        print(f"🚀 Executing on Linux/macOS: {full_command}")
        stdin, stdout, stderr = client.exec_command(full_command)
        stdout.channel.recv_exit_status()  # Wait for completion

        # Check if file exists
        for _ in range(30):
            stdin, stdout, _ = client.exec_command(f"test -f {remote_snapshot_path} && echo EXISTS")
            if "EXISTS" in stdout.read().decode():
                print("📁 Snapshot file detected.")
                break
            time.sleep(1)
        else:
            return JSONResponse(content={"error": "Snapshot not found after waiting."}, status_code=500)

        # Read and transfer file
        sftp = client.open_sftp()
        with sftp.open(remote_snapshot_path, 'rb') as remote_file:
            file_data = remote_file.read()

        local_path = SNAPSHOT_DIR / snapshot_filename
        with open(local_path, 'wb') as f:
            f.write(file_data)

        print(f"✅ Snapshot pulled and saved to: {local_path}")
        return {
            "status": "success",
            "message": f"Snapshot from {vm_ip} collected and uploaded!",
            "vm_hostname": vm_ip
        }

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(content={"error": f"SSH collection failed: {str(e)}"}, status_code=500)
    finally:
        client.close()


        
        
@app.get("/list_snapshots")
async def list_snapshots():
    try:
        snapshots = []
        for file in SNAPSHOT_DIR.glob("*.json"):
            snapshots.append(file.name)
        return {"snapshots": snapshots}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/download_snapshot/{filename}")
async def download_snapshot(filename: str):
    file_path = SNAPSHOT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, filename=filename, media_type='application/json')
    else:
        return JSONResponse(content={"error": "File not found."}, status_code=404)
        
@app.post("/flag")
async def flag_feedback(payload: dict = Body(...)):
    try:
        # Save flagged content for review or retraining
        with open("flagged_feedback.jsonl", "a") as f:
            f.write(json.dumps(payload) + "\n")
        return {"message": "Feedback recorded"}
    except Exception as e:
        print("Feedback error:", e)
        return {"error": str(e)}
        
@app.post("/ocr")
async def ocr_image(payload: dict = Body(...)):
    base64_image = payload.get("base64_image")
    if not base64_image:
        return JSONResponse(status_code=400, content={"error": "No image provided"})

    try:
        image_data = base64.b64decode(base64_image.split(",")[-1])
        image = Image.open(io.BytesIO(image_data))
        raw_text = pytesseract.image_to_string(image)
        cleaned_text = clean_ocr_text(raw_text)
        return {"text": cleaned_text}
    except Exception as e:
        print("❌ OCR error:", e)
        return JSONResponse(status_code=500, content={"error": "OCR processing failed"})
        
        
@app.post("/read_log")
async def read_log_endpoint(payload: dict = Body(...)):
    path = payload.get("path")
    if not path:
        return JSONResponse(status_code=400, content={"error": "No log path provided"})

    try:
        log_content = read_log_file_safely(path)
        return {"content": log_content}
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


        
# --- Utilities ---
def read_log_file_safely(path, max_lines=200000):
    """
    Safely reads the last `max_lines` from a log file to avoid memory overload.
    
    Args:
        path (str): Path to the log file.
        max_lines (int): Number of lines to read from the end (default 200k).

    Returns:
        str: A string of the last N lines of the log.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return ''.join(lines[-max_lines:])
    except Exception as e:
        print(f"⚠️ Error reading log file at {path}: {e}")
        return ""


def normalize_log_block(block):
    # Remove timestamps and join for deduplication
    clean = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}(?:[,\.]\d+)?', '', block)
    clean = re.sub(r'\d{2}:\d{2}:\d{2}(?:[,\.]\d+)?', '', clean)
    return clean.strip()

def extract_important_log_blocks(log_text, keywords=None, max_blocks=30):
    """
    Extracts important log blocks, including multi-line stack traces,
    filters by keyword, deduplicates by content (ignoring timestamps),
    and limits output to the latest N unique blocks.
    """
    keywords = keywords or ['ERROR', 'Exception', 'Traceback', 'CRITICAL', 'Failed', 'Caused by']
    lines = log_text.splitlines()

    blocks = []
    current_block = []
    seen = set()

    def commit_block():
        if current_block:
            full_block = "\n".join(current_block).strip()
            norm = normalize_log_block(full_block)
            if norm not in seen:
                seen.add(norm)
                blocks.append(full_block)
            current_block.clear()

    for line in lines:
        if any(k in line for k in keywords):
            commit_block()  # Save previous block before starting new one
            current_block.append(line)
        elif current_block and (line.startswith(" ") or line.startswith("\t") or line.strip() == ""):
            # Likely a stack trace or continuation
            current_block.append(line)
        else:
            commit_block()

    commit_block()  # Final block

    return "\n\n---\n\n".join(blocks[-max_blocks:])

def estimate_token_count(text):
    enc = get_encoding("cl100k_base")
    return len(enc.encode(text))

def read_log_file(path):
    try:
        if os.path.exists(path) and path.endswith('.log'):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print("⚠️ Failed to read log:", e)
    return ""


def extract_text_from_screenshot(base64_image):
    try:
        image_data = base64.b64decode(base64_image.split(",")[-1])
        image = Image.open(io.BytesIO(image_data))
        raw_text = pytesseract.image_to_string(image)
        cleaned_text = clean_ocr_text(raw_text)
        return cleaned_text
    except Exception as e:
        print("Error extracting text from screenshot:", e)
        return ""
        
def clean_ocr_text(text):
    # Normalize Unicode (e.g., accented characters)
    text = unicodedata.normalize("NFKD", text)

    # Remove non-printable characters (keep ASCII)
    text = re.sub(r'[^\x20-\x7E]+', '', text)

    # Collapse multiple spaces, remove leading/trailing whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text
    
def generate_initial_prompt(payload):
    diff = payload.get("diff", {})
    error_message = payload.get("error_message", "")
    screenshot_text = payload.get("error_screenshot_text", "")
    log_content = payload.get("log_content", "")

    return f"""
You are an expert in diagnosing system and application configuration issues.

Analyze the following:
- DeepDiff data: {json.dumps(diff, indent=2)}
- Error message (if any): {error_message or 'None'}
- OCR from screenshot (if any): {screenshot_text or 'None'}
- Relevant logs (if any): {log_content or 'None'}

Please summarize what might have gone wrong, and guide what else should be collected if not enough information is available.
"""

def compile_session_prompt(session):
    messages = [
        {"role": "system", "content": "You are a highly skilled IT troubleshooting assistant helping diagnose configuration issues across systems."},
        {"role": "user", "content": generate_initial_prompt(session.initial_input)}
    ]
    for ai_msg, user_msg in zip(session.ai_messages, session.user_followups):
        messages.append({"role": "assistant", "content": ai_msg["content"]})
        messages.append({"role": "user", "content": user_msg["content"]})
    return messages
    
"""
def call_openai_with_prompt(messages):
    if isinstance(messages, str):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": messages}
        ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content.strip()
"""

