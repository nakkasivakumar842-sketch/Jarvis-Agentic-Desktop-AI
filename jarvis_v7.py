import os
import datetime
import requests
import json
import asyncio
import pygame
import pyautogui
import psutil 
import feedparser
import threading
import time
import wikipedia
import warnings
import speech_recognition as sr
from ddgs import DDGS
from AppOpener import open as app_open
from memory_manager import JadaalMemory
import webbrowser
import time
import pytesseract
from PIL import ImageGrab

# Point Python to your newly installed optical drivers
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

warnings.filterwarnings("ignore", category=ResourceWarning)

class JarvisSystem:
    def __init__(self, ui_callback):
        self.update_ui = ui_callback
        pygame.mixer.init()
        
        # Audio Initialization
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        print("[System] Initializing ChromaDB Vector Memory...")
        self.memory = JadaalMemory()
        
        self.chat_history = [{"role": "system", "content": "You are Jarvis, a brilliant, highly concise AI assistant. You refer to the user as 'Sir'. Keep responses under two sentences. The current year is 2026."}]

    def speak(self, text):
        print(f"\n\033[92mJarvis: {text}\033[0m\n")
        self.update_ui("SPEAKING") 
        
        # Safe Audio Threading
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._generate_and_play_audio(text))
        loop.close() 
        self.update_ui("IDLE")

    async def _generate_and_play_audio(self, text):
        import edge_tts
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural", rate="+0%")
        audio_file = "jarvis_response.mp3"
        await communicate.save(audio_file)
        
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        try:
            os.remove(audio_file)
        except Exception: 
            pass 

    def analyze_system_hardware(self):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        batt_percent = battery.percent if battery else "Unknown"
        return f"Diagnostic complete, Sir. CPU load is at {cpu} percent. Memory utilization is {ram} percent. Battery power is at {batt_percent} percent."

    def fetch_weather(self, city="Gollaprolu"):
        self.update_ui("THINKING")
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_data = requests.get(geo_url, timeout=5).json()
            if not geo_data.get("results"): return f"Sir, I could not locate coordinates for {city}."
            lat, lon = geo_data["results"][0]["latitude"], geo_data["results"][0]["longitude"]
            
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_data = requests.get(weather_url, timeout=5).json()
            return f"The current temperature in {city} is {weather_data['current_weather']['temperature']} degrees Celsius."
        except Exception:
            return "Sir, my connection to the external meteorological servers is currently offline."

    def agentic_web_search(self, query):
        self.update_ui("THINKING")
        clean_query = query.replace("search the internet", "").replace("look up", "").strip()
        live_data = ""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(clean_query, max_results=3))
            if results: live_data = " ".join([r['body'] for r in results])
        except Exception: pass

        if not live_data:
            try:
                wikipedia.set_user_agent("JarvisHUD/1.0")
                wiki_search = wikipedia.search(clean_query)
                if wiki_search: live_data = wikipedia.summary(wiki_search[0], sentences=4, auto_suggest=False)
            except Exception: return "Sir, my connection to external web servers was severed."

        prompt = f"INSTRUCTION: Answer using ONLY this Live Web Data: {live_data}\nUser Question: {clean_query}"
        return self.process_with_ai(prompt, save_to_memory=False)

    def requires_internet(self, query):
        keywords = ["who is", "weather", "temperature", "price", "news", "score", "cm", "pm", "latest", "match"]
        return any(key in query for key in keywords)

    def process_with_ai(self, user_text, save_to_memory=True):
        self.update_ui("THINKING")
        full_prompt = user_text
        
        if save_to_memory:
            past_context = self.memory.search_memories(user_text, limit=2)
            if past_context:
                full_prompt = f"{past_context}\nUser's current message: {user_text}"

        self.chat_history.append({"role": "user", "content": full_prompt})
        
        try:
            # ERROR-PROOF OLLAMA CALL
            response = requests.post("http://localhost:11434/api/chat", json={"model": "llama3", "messages": self.chat_history, "stream": False}, timeout=60)
            response_data = response.json()
            
            if "error" in response_data:
                error_msg = response_data["error"]
                print(f"\n[Ollama Server Error]: {error_msg}")
                return f"Sir, my cognitive engine encountered an error: {error_msg}"
                
            ai_reply = response_data["message"]["content"]
            
            if save_to_memory:
                self.chat_history.append({"role": "assistant", "content": ai_reply})
                self.memory.store_interaction(user_text, ai_reply)
                self.chat_history = [self.chat_history[0]] + self.chat_history[-4:]
            else:
                self.chat_history.pop() 
                
            return ai_reply
        except requests.exceptions.ConnectionError:
            return "Sir, my local neural node is offline. Please ensure Ollama is running."
        except Exception as e:
            return "Sir, I am experiencing a critical fault in my neural link."

    def execute_hardcoded_action(self, command):
        import subprocess
        import pyautogui
        import webbrowser
        import time
        import datetime

        if "clear memory" in command:
            self.memory.wipe_memory()
            self.speak("Vector database wiped, Sir. Matrix is clear.")
            return True
        elif any(word in command for word in ["diagnostic", "hardware", "cpu", "battery"]):
            self.speak(self.analyze_system_hardware())
            return True
        elif command == "time" or "what is the time" in command:
            self.speak(f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}, Sir.")
            return True
        elif "date" in command:
            self.speak(f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}, Sir.")
            return True
        elif "weather" in command or "temperature" in command:
            target_city = "Gollaprolu"
            if " in " in command: target_city = command.split(" in ")[-1].replace("?", "").strip().title()
            self.speak(self.fetch_weather(target_city))
            return True
        
        # --- FIX: HARDWARE & APPLICATION CLOSING SYSTEM ---
        elif "close all tabs" in command:
            self.speak("Terminating all active browser processes, Sir.")
            # Hard-kills processes of major browsers to wipe out all tabs instantly
            target_browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"]
            for browser in target_browsers:
                subprocess.run(["taskkill", "/f", "/im", browser], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True

        elif "close all apps" in command or "close all applications" in command:
            self.speak("Executing master system clearance routine.")
            # Advanced PowerShell pipeline: Selects only tasks with active visible windows,
            # explicitly ignoring Python, CMD, and basic Windows shell processes so Jarvis doesn't crash himself.
            ps_script = 'Get-Process | Where-Object {$_.MainWindowTitle -and $_.ProcessName -notlike "python*" -and $_.ProcessName -notlike "cmd*" -and $_.ProcessName -notlike "powershell*" -and $_.ProcessName -notlike "explorer"} | Stop-Process -Force'
            subprocess.run(["powershell", "-Command", ps_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True

        elif command.startswith("close "):
            target_app = command.replace("close ", "").strip().lower()
            
            # Map casual names to their actual underlying Windows .exe handles
            app_exe_map = {
                "spotify": "Spotify.exe",
                "chrome": "chrome.exe",
                "edge": "msedge.exe",
                "notepad": "notepad.exe",
                "discord": "Discord.exe",
                "vlc": "vlc.exe",
                "browser": "chrome.exe"
            }
            
            exe_target = app_exe_map.get(target_app, f"{target_app}.exe")
            
            # Force kill the target process signature
            kill_execution = subprocess.run(["taskkill", "/f", "/im", exe_target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if "SUCCESS" in kill_execution.stdout:
                self.speak(f"Successfully terminated {target_app.title()}, Sir.")
            else:
                # Secondary Fallback: If taskkill fails, use an active Alt+F4 command interrupt
                pyautogui.hotkey('alt', 'f4')
                self.speak(f"Forcing closure on active window loop.")
            return True

        # --- WINDOWS WINDOW MANAGEMENT ---
        elif "minimize all" in command or "show desktop" in command or "minimise all" in command:
            pyautogui.hotkey('win', 'd')
            self.speak("Minimizing environment windows.")
            return True
        elif "close this window" in command or "close application" in command:
            pyautogui.hotkey('alt', 'f4')
            self.speak("Application terminated.")
            return True
        elif "close tab" in command:
            pyautogui.hotkey('ctrl', 'w')
            self.speak("Tab closed.")
            return True
        elif "take a screenshot" in command or "capture screen" in command:
            filename = f"screenshot_{int(time.time())}.png"
            pyautogui.screenshot(filename)
            self.speak(f"Screenshot successfully captured and saved as {filename}.")
            return True
        elif "youtube" in command and "search" in command:
            query = command.split("search for")[-1].strip() if "search for" in command else command.split("search")[-1].strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            self.speak(f"Searching YouTube for {query}.")
            return True
        elif "open " in command and "website" not in command:
            app_name = command.replace("open ", "").strip()
            self.speak(f"Attempting to launch {app_name}.")
            try: app_open(app_name, match_closest=True)
            except: pass
            return True
        elif "volume up" in command:
            pyautogui.press("volumeup", presses=10)
            self.speak("Audio levels increased.")
            return True
        elif "volume down" in command:
            pyautogui.press("volumedown", presses=10)
            self.speak("Audio levels decreased.")
            return True
            
        return False

    # --- THE AUTONOMOUS WAKE WORD ENGINE ---
    # --- THE CONTINUOUS WAKE WORD ENGINE ---
    def start_wake_word_loop(self):
        print("\n[SYSTEM] Continuous Wake Word Engine Online. Listening...")
        
        with self.mic as source:
            # Calibrate to background noise once
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Set the pause threshold a bit higher so it doesn't cut you off mid-sentence
            self.recognizer.pause_threshold = 1.0 
            
            while True:
                try:
                    # Listen in longer chunks, constantly
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                    
                    # Convert the entire block of speech to text
                    full_text = self.recognizer.recognize_google(audio).lower()
                    
                    # Check if 'jarvis' is ANYWHERE in that sentence
                    if "jarvis" in full_text:
                        # Slice out the wake word and extract the actual command
                        command = full_text.split("jarvis", 1)[-1].strip()
                        
                        # If you just said "Jarvis", wait for a command
                        if not command:
                            print("\n[WAKE WORD DETECTED] Awaiting command...")
                            self.update_ui("LISTENING", "Awaiting command...")
                            try:
                                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                                command = self.recognizer.recognize_google(audio).lower()
                            except sr.WaitTimeoutError:
                                print("[SYSTEM] No command received.")
                                self.update_ui("ONLINE", "Core Matrix Online...")
                                continue
                            except sr.UnknownValueError:
                                continue
                                
                        print(f"\n\033[94mUser Voice Command: '{command}'\033[0m") 
                        self.update_ui("THINKING", f"Processing: '{command}'")
                        
                        if "shut down" in command or "go to sleep" in command:
                            self.speak("Powering down cognitive subroutines. Goodbye, Sir.")
                            os._exit(0)

                        action_taken = self.execute_hardcoded_action(command)
                        if not action_taken:
                            if self.requires_internet(command): reply = self.agentic_web_search(command)
                            else: reply = self.process_with_ai(command)
                            self.speak(reply)
                            
                        # Reset UI after speaking
                        self.update_ui("ONLINE", "Core Matrix Online...")
                        
                except sr.UnknownValueError:
                    continue # Heard noise, but not words
                except Exception as e:
                    continue

if __name__ == "__main__":
    print("[SYSTEM] Direct execution disabled. Please launch via 'jarvis_ui.py'.")