import webview
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import sys

# Import the Brain
from jarvis_v7 import JarvisSystem

app = FastAPI()

class UserInput(BaseModel):
    prompt: str

# Global reference so the updater can find the window
jarvis_window = None

# --- THE REAL UI BRIDGE ---
# This safely pipes Python events directly into your Holographic HTML panel
def real_ui_updater(status, message=""):
    global jarvis_window
    if jarvis_window:
        try:
            # Escape quotes so Javascript doesn't break when reading the command
            safe_message = message.replace("'", "\\'").replace('"', '\\"')
            jarvis_window.evaluate_js(f"updateStatus('{status}', '{safe_message}')")
        except Exception as e:
            pass

print("[SYSTEM] Booting Cognitive Core into Background API...")

# Inject the real UI updater into the engine
jarvis_engine = JarvisSystem(ui_callback=real_ui_updater)

# --- START THE WAKE WORD ENGINE IN BACKGROUND ---
listen_thread = threading.Thread(target=jarvis_engine.start_wake_word_loop, daemon=True)
listen_thread.start()

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
def handle_chat(user_input: UserInput):
    command = user_input.prompt.lower()
    print(f"\n[API] Received Text Command: {command}")
    
    reply = ""
    action_taken = jarvis_engine.execute_hardcoded_action(command)
    
    if action_taken:
        reply = "[System Action Executed]"
    else:
        if jarvis_engine.requires_internet(command):
            reply = jarvis_engine.agentic_web_search(command)
        else:
            reply = jarvis_engine.process_with_ai(command)
            
        # Speak the reply aloud while returning it to the screen
        threading.Thread(target=jarvis_engine.speak, args=(reply,), daemon=True).start()

    return {"reply": reply}

def start_server():
    # Hide Uvicorn logs so the terminal stays clean
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Launching JARVIS Holographic Orb...")
    
    jarvis_window = webview.create_window(
        title="Jarvis", 
        url="http://127.0.0.1:8000", 
        width=400, 
        height=550, 
        frameless=True,       
        transparent=True,     
        easy_drag=True,      
        on_top=True
    )
    
    # Run PyQt5 Engine
    webview.start(gui="qt") 
    
    # Kill background threads on close
    os._exit(0)