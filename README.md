# Jarvis-Agentic-Desktop-AI
Jarvis is a free, fully autonomous AI desktop assistant built in Python. Powered by Llama 3 and LangGraph, it acts as a proactive agent. It listens offline, speaks instantly, and reads your screen using OCR. It physically controls your PC using PowerShell to manage apps, operating through a custom holographic desktop interface.

# 🧠 Jarvis : Local Agentic AI Desktop Assistant

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Llama 3](https://img.shields.io/badge/Llama_3-0466C8?style=for-the-badge&logo=meta&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF4F00?style=for-the-badge&logo=chroma&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

Jarvis is a highly advanced, multi-modal desktop AI assistant engineered from the ground up to operate as an independent, proactive system. 

Unlike standard chat wrappers, Jadaal is built on an **agentic cyclical workflow** and runs **100% locally and offline**. It can perceive its environment (Optical Screen Awareness), remember past interactions (Vector Memory), and execute physical actions on the host Windows machine (PowerShell/UI Automation) entirely hands-free, without relying on external API keys.

<p align="center">
  <i></i>
</p>

## 🚀 Key Architectural Features

* **Cyclical Agentic Reasoning:** Powered by **LangGraph**, the cognitive core doesn't just answer questions; it routes logic through conditional nodes. The AI dynamically chooses when to call external tools, check the local system, or access its memory before responding, with built-in infinite-loop protection.
* **Continuous Audio Pipeline:** Engineered a zero-latency, multi-threaded audio buffer using **openWakeWord** and `SpeechRecognition`. The system listens locally and offline, seamlessly slicing continuous speech after the wake word to allow for fluid, conversational commands.
* **Optical Screen Awareness (OCR):** Integrated **PyTesseract** to give the AI "eyes." The system can silently snapshot the active desktop, extract readable text, and feed it to the local LLM to summarize or answer contextual questions about exactly what the user is looking at.
* **Vectorized Long-Term Memory:** Utilizes **ChromaDB** for local Retrieval-Augmented Generation (RAG). The assistant mathematically embeds every interaction, allowing it to silently retrieve relevant past context before generating a new response—keeping 100% of data private.
* **Hardware-Accelerated Holographic UI:** Replaced standard console outputs with a borderless, interactive HTML/JS matrix rendered natively on the Windows desktop via **PyWebView** and the **PyQt5** engine, fully bridged to the Python backend via a **FastAPI** webhook server.
* **Physical Desktop Automation:** Hardwired deep OS hooks using `pyautogui` and advanced PowerShell scripting, allowing the AI to physically manage the desktop environment (e.g., forcing process terminations, wiping browser tabs, and checking hardware diagnostics).

## 🛠️ The Tech Stack

* **Cognitive Core:** Meta Llama 3 (Executed strictly locally via Ollama)
* **Orchestration:** LangChain / LangGraph
* **Memory Integration:** ChromaDB (Local Vector Store)
* **Vision / Senses:** PyTesseract OCR, Pillow
* **Voice Engine:** openWakeWord (Offline), edge-tts (Synthesis), SpeechRecognition
* **User Interface:** PyQt5, PyWebView, FastAPI, Uvicorn, HTML/CSS/JS
* **System Control:** Subprocess (PowerShell), PyAutoGUI, Psutil

## ⚙️ Installation & Boot Sequence

**Prerequisites:**
* Python 3.10+
* [Ollama](https://ollama.com/) installed locally to run the Llama 3 model.
* Tesseract OCR drivers installed locally (Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`).

1. Clone the repository and install the dependencies:

   git clone [https://github.com/YourUsername/Jadaal-Agentic-AI.git](https://github.com/YourUsername/Jadaal-Agentic-AI.git)
   cd Jadaal-Agentic-AI
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
