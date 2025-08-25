# -------------------
# JARVIS 3.0 - AI-ENHANCED PYTHON VOICE ASSISTANT WITH GEMINI
# -------------------

# --- Core Libraries ---
import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import subprocess
import json
import sys
import inspect
import time
import random
import datetime
import threading
import difflib
from pathlib import Path

# --- Feature-Specific Libraries ---
import pywhatkit
import wikipedia
import requests

# --- AI Integration ---
import google.generativeai as genai

# --- Optional Libraries with Graceful Handling ---
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# --- NEW: Libraries for new features ---
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

try:
    import winshell
    WINSHELL_AVAILABLE = True
except ImportError:
    WINSHELL_AVAILABLE = False


# --- Optional Hardware Control Libraries (Windows Only) ---
try:
    from ctypes import cast, POINTER, windll
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_INSTALLED = True
except ImportError:
    PYCAW_INSTALLED = False

# --- Email Libraries ---
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# -------------------
# 1. INITIALIZATION AND CONFIGURATION
# -------------------

# Initialize Speech Recognition
recognizer = sr.Recognizer()

# Global TTS engine for better performance
tts_engine = None

# AI Configuration
GEMINI_API_KEY = "AIzaSyCfQBCOfZbwnce3Dn82QBz7RoMRCi6Ain8" # IMPORTANT: Replace with your actual API key
ai_model = None

def initialize_ai():
    """Initialize Gemini AI with enhanced error handling."""
    global ai_model
    try:
        # --- FIX: Use the correct, current model name ---
        genai.configure(api_key=GEMINI_API_KEY)
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test the AI connection
        test_response = ai_model.generate_content("Hello, respond with 'AI initialized successfully'")
        if test_response.text:
            print("✅ Gemini AI initialized successfully")
            return True
        else:
            print("❌ AI test failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize Gemini AI: {e}")
        return False

def ask_ai(query, context="general"):
    """Enhanced AI query function with context awareness."""
    if not ai_model:
        return "AI is not available at the moment."
    
    try:
        # Create context-aware prompts
        system_context = f"""
        You are JARVIS, an advanced AI voice assistant. You should:
        - Be helpful, concise, and conversational
        - Provide practical answers that can be spoken aloud
        - Keep responses under 100 words unless specifically asked for details
        - Be friendly but professional
        - Context: {context}
        
        User query: {query}
        """
        
        response = ai_model.generate_content(system_context)
        
        if response.text:
            return response.text.strip()
        else:
            return "I'm having trouble processing that request."
            
    except Exception as e:
        print(f"AI Error: {e}")
        return "I encountered an error while processing your request."

def ai_task_analyzer(command):
    """Uses AI to analyze and suggest how to handle unknown commands."""
    if not ai_model:
        return None
    
    try:
        analysis_prompt = f"""
        Analyze this voice command and suggest how a computer assistant should handle it:
        Command: "{command}"
        
        Respond with one of these categories:
        1. SEARCH - if it's asking for information that needs web search
        2. CALCULATE - if it involves math or calculations
        3. OPEN_APP - if it's asking to open an application
        4. SYSTEM - if it's about system control (volume, time, etc.)
        5. CONVERSATION - if it's a general question or conversation
        6. UNKNOWN - if unclear
        
        Format: CATEGORY|explanation
        """
        
        response = ai_model.generate_content(analysis_prompt)
        if response.text:
            return response.text.strip()
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
    
    return None

def initialize_tts():
    """Initialize the TTS engine once at startup with better error handling."""
    global tts_engine
    try:
        # Try different TTS engines
        engines = ['sapi5', 'nsss', 'espeak']
        
        for engine_name in engines:
            try:
                tts_engine = pyttsx3.init(engine_name)
                voices = tts_engine.getProperty('voices')
                
                if voices and len(voices) > 0:
                    # Set voice properties
                    tts_engine.setProperty('voice', voices[0].id)
                    tts_engine.setProperty('rate', 180)  # Speed of speech
                    tts_engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)
                    
                    # Test the engine
                    tts_engine.say("TTS engine initialized")
                    tts_engine.runAndWait()
                    
                    print(f"✅ TTS initialized successfully with {engine_name}")
                    return True
                    
            except Exception as e:
                print(f"❌ Failed to initialize {engine_name}: {e}")
                continue
        
        print("❌ No TTS engines available")
        return False
        
    except Exception as e:
        print(f"❌ TTS initialization failed: {e}")
        return False

def speak(text, priority=False):
    """Enhanced speech function with multiple fallback methods."""
    print(f"Jarvis: {text}")
    
    # Method 1: Direct Windows SAPI (most reliable)
    if sys.platform == "win32":
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
            return  # Success, exit function
        except ImportError:
            print("🔄 win32com not available, trying pyttsx3...")
        except Exception as e:
            print(f"❌ Windows SAPI failed: {e}")
    
    # Method 2: pyttsx3 with forced execution
    try:
        if tts_engine is not None:
            # Stop any ongoing speech
            try:
                tts_engine.stop()
            except:
                pass
            
            # Set properties
            tts_engine.setProperty('rate', 180 if not priority else 200)
            tts_engine.setProperty('volume', 1.0)
            
            # Clear queue and speak
            tts_engine.say(text)
            tts_engine.runAndWait()
            
            # Force completion
            import time
            time.sleep(0.1)
            return
            
    except Exception as e:
        print(f"❌ pyttsx3 failed: {e}")
    
    # Method 3: Fresh pyttsx3 instance
    try:
        print("🔄 Creating fresh TTS instance...")
        fresh_engine = pyttsx3.init()
        fresh_engine.setProperty('rate', 180)
        fresh_engine.setProperty('volume', 1.0)
        fresh_engine.say(text)
        fresh_engine.runAndWait()
        fresh_engine.stop()
        del fresh_engine
        return
    except Exception as e:
        print(f"❌ Fresh pyttsx3 failed: {e}")
    
    # Method 4: PowerShell command (Windows)
    if sys.platform == "win32":
        try:
            print("🔄 Using PowerShell TTS...")
            import subprocess
            escaped_text = text.replace("'", "''").replace('"', '""')
            cmd = f'''powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak('{escaped_text}')"'''
            subprocess.run(cmd, shell=True, capture_output=True)
            return
        except Exception as e:
            print(f"❌ PowerShell TTS failed: {e}")
    
    # Method 5: System TTS commands
    try:
        if sys.platform == "darwin":  # macOS
            os.system(f'say "{text}"')
        elif sys.platform.startswith("linux"):  # Linux
            os.system(f'espeak "{text}" 2>/dev/null || echo "{text}" | festival --tts')
        else:
            print("❌ No TTS method available for this platform")
    except Exception as e:
        print(f"❌ System TTS failed: {e}")
        print("❌ ALL TTS METHODS FAILED!")
        print("💡 Try: pip install pywin32")

def load_config():
    """Enhanced configuration loader with AI settings and user memory."""
    try:
        with open('config.json', 'r') as f:
            config_data = json.load(f)

        # --- FIX: Ensure user_memory key exists ---
        if "user_memory" not in config_data:
            config_data["user_memory"] = {}
            with open('config.json', 'w') as f:
                json.dump(config_data, f, indent=4)

        return config_data

    except FileNotFoundError:
        speak("Configuration file not found. Creating a comprehensive config file for you.")
        template = {
            "app_paths": {
                "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                "vscode": f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
                "discord": f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Discord\\Update.exe",
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "spotify": f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Spotify\\Spotify.exe",
                "steam": "C:\\Program Files (x86)\\Steam\\steam.exe"
            },
            "api_keys": {
                "openweathermap": "YOUR_WEATHER_API_KEY_HERE",
                "newsapi": "YOUR_NEWS_API_KEY_HERE",
                "gemini": GEMINI_API_KEY
            },
            "email_config": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "your_email@gmail.com",
                "password": "your_app_password"
            },
            "preferences": {
                "wake_word": "jarvis",
                "default_browser": "chrome",
                "voice_rate": 180,
                "voice_volume": 0.9,
                "ai_enabled": True,
                "ai_fallback": True
            },
            "user_memory": {}
        }
        with open('config.json', 'w') as f:
            json.dump(template, f, indent=4)
        return template

# Load configuration
CONFIG = load_config()

# -------------------
# 2. ENHANCED AI-POWERED FEATURES
# -------------------

def ai_general_query(query):
    """Handles general AI queries and conversations."""
    speak("Let me think about that...")
    response = ask_ai(query, "general conversation")
    speak(response)

def ai_smart_search(query):
    """AI-enhanced search that decides between web search or direct answer."""
    analysis = ask_ai(f"Should I search the web for '{query}' or can you answer it directly? If you can answer directly, provide the answer. If web search is needed, respond with 'WEB_SEARCH_NEEDED'", "search decision")
    
    if "WEB_SEARCH_NEEDED" in analysis:
        google_search(query)
    else:
        speak(analysis)

def ai_explain_topic(topic):
    """Uses AI to explain complex topics in simple terms."""
    speak("Let me explain that for you...")
    explanation = ask_ai(f"Explain {topic} in simple terms that can be easily understood when spoken aloud. Keep it concise but informative.", "educational explanation")
    speak(explanation)

def ai_creative_task(task):
    """Handles creative tasks like writing, storytelling, etc."""
    speak("I'll work on that creative task for you...")
    result = ask_ai(f"Help with this creative task: {task}. Provide a response suitable for voice delivery.", "creative task")
    speak(result)

def ai_problem_solver(problem):
    """Uses AI to help solve problems or provide advice."""
    speak("Let me analyze that problem...")
    solution = ask_ai(f"Help solve this problem or provide advice: {problem}. Give practical, actionable advice.", "problem solving")
    speak(solution)

def ai_code_helper(request):
    """AI assistance for coding tasks."""
    speak("I'll help you with that coding task...")
    code_help = ask_ai(f"Provide coding help for: {request}. Give a clear, concise explanation suitable for voice delivery.", "coding assistance")
    speak(code_help)

def get_current_time():
    """Gets and speaks the current time with AI enhancement."""
    now = datetime.datetime.now()
    time_string = now.strftime("%I:%M %p")
    date_string = now.strftime("%A, %B %d, %Y")
    
    basic_time = f"The current time is {time_string} on {date_string}"
    
    # Add AI context if available
    if ai_model and CONFIG.get("preferences", {}).get("ai_enabled", True):
        try:
            context = ask_ai(f"The current time is {time_string} on {date_string}. Add a brief, friendly comment about the time of day.", "time context")
            speak(f"{basic_time}. {context}")
        except:
            speak(basic_time)
    else:
        speak(basic_time)

def get_system_status():
    """Enhanced system status with AI interpretation."""
    if not PSUTIL_AVAILABLE:
        speak("System monitoring not available. Please install psutil: pip install psutil")
        return
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        basic_status = f"System status: CPU usage is {cpu_percent}%, RAM usage is {memory.percent}%, and disk usage is {disk.percent}%"
        
        # Add AI interpretation
        if ai_model and CONFIG.get("preferences", {}).get("ai_enabled", True):
            try:
                interpretation = ask_ai(f"Interpret these system stats: CPU {cpu_percent}%, RAM {memory.percent}%, Disk {disk.percent}%. Provide a brief assessment of system health.", "system analysis")
                speak(f"{basic_status}. {interpretation}")
            except:
                speak(basic_status)
        else:
            speak(basic_status)
            
    except Exception as e:
        speak("Unable to retrieve system status")

def take_screenshot():
    """Takes a screenshot and saves it."""
    if not PYAUTOGUI_AVAILABLE:
        speak("Screenshot feature not available. Please install pyautogui: pip install pyautogui")
        return
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        speak(f"Screenshot saved as {filename}")
    except Exception as e:
        speak("Failed to take screenshot")

def take_picture(frame):
    """Saves a single frame from the camera feed as a picture."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"picture_{timestamp}.png"
        cv2.imwrite(filename, frame)
        speak(f"Picture saved as {filename}")
    except Exception as e:
        speak("Sorry, I failed to save the picture.")

def open_camera():
    """Opens an interactive camera feed."""
    if not CV2_AVAILABLE:
        speak("Camera features require OpenCV. Please install it by running: pip install opencv-python")
        return

    speak("Camera is activating. Say 'take picture' to capture, or 'close camera' to exit.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("I could not access the camera.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            speak("I lost the camera feed.")
            break

        cv2.imshow('Jarvis Camera', frame)

        # Listen for a command in a non-blocking way
        command = listen(timeout=1, phrase_time_limit=2)
        if command:
            if "take picture" in command or "capture" in command:
                take_picture(frame)
            elif "close camera" in command or "exit" in command:
                speak("Closing camera.")
                break

        # Allow closing with the 'q' key as a backup
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def open_camera_alternative():
    """Opens camera using system default camera app."""
    try:
        speak("Opening system camera app")
        
        if sys.platform == "win32":
            # Windows Camera app
            try:
                subprocess.run("start microsoft.windows.camera:", shell=True, check=True)
                speak("Camera app opened successfully")
            except subprocess.CalledProcessError:
                # Fallback to older Windows camera
                try:
                    os.system("start /B microsoft.windows.camera:")
                    speak("Camera opened")
                except:
                    speak("Unable to open camera. Please open it manually from your start menu")
        
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", "-a", "Photo Booth"], check=True)
            speak("Photo Booth camera opened")
        
        else:  # Linux
            try:
                # Try different camera applications
                camera_apps = ["cheese", "guvcview", "camorama", "kamoso"]
                for app in camera_apps:
                    try:
                        subprocess.run([app], check=True)
                        speak(f"Camera opened with {app}")
                        return
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                speak("No camera application found. Please install cheese or guvcview")
            except Exception:
                speak("Unable to open camera on this system")
                
    except Exception as e:
        speak("Sorry, I couldn't access the camera")

def get_news():
    """Fetches latest news headlines with AI summarization."""
    api_key = CONFIG.get("api_keys", {}).get("newsapi")
    if not api_key or "YOUR_NEWS_API_KEY" in api_key:
        speak("News API key not configured. Let me get you some general news information instead.")
        ai_news = ask_ai("What are some important current events or news topics I should know about today?", "news summary")
        speak(ai_news)
        return
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
        response = requests.get(url)
        news_data = response.json()
        
        if news_data["status"] == "ok":
            articles = news_data["articles"][:3]  # Top 3 headlines
            headlines = [article['title'] for article in articles]
            
            speak("Here are the top news headlines:")
            for i, headline in enumerate(headlines, 1):
                speak(f"Headline {i}: {headline}")
            
            # AI summary if available
            if ai_model:
                try:
                    summary = ask_ai(f"Provide a brief commentary on these news headlines: {', '.join(headlines)}", "news analysis")
                    speak(f"AI Analysis: {summary}")
                except:
                    pass
        else:
            speak("Unable to fetch news at the moment")
    except Exception as e:
        speak("Failed to get news updates")

def send_email(recipient, subject, body):
    """Sends an email (requires email configuration)."""
    if not EMAIL_AVAILABLE:
        speak("Email functionality not available")
        return
    
    email_config = CONFIG.get("email_config", {})
    if not all(key in email_config for key in ["email", "password"]):
        speak("Email not configured. Please update config.json")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = email_config["email"]
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
        server.starttls()
        server.login(email_config["email"], email_config["password"])
        server.send_message(msg)
        server.quit()
        
        speak(f"Email sent to {recipient}")
    except Exception as e:
        speak("Failed to send email")

def set_reminder(minutes, message):
    """Sets a reminder that will speak after specified minutes."""
    def remind():
        time.sleep(minutes * 60)
        speak(f"Reminder: {message}", priority=True)
    
    thread = threading.Thread(target=remind)
    thread.daemon = True
    thread.start()
    speak(f"Reminder set for {minutes} minutes from now")

def get_joke():
    """Tells a random joke with AI enhancement."""
    if ai_model and CONFIG.get("preferences", {}).get("ai_enabled", True):
        try:
            ai_joke = ask_ai("Tell me a clean, funny joke that would be good for a voice assistant to tell.", "humor")
            speak(ai_joke)
            return
        except:
            pass
    
    # Fallback to predefined jokes
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "Why did the math book look so sad? Because it had too many problems!"
    ]
    speak(random.choice(jokes))

def calculate(expression):
    """Enhanced mathematical calculations with AI assistance."""
    try:
        # Basic safety: only allow certain characters
        allowed_chars = "0123456789+-*/.() "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            speak(f"The answer is {result}")
            
            # AI explanation for complex calculations
            if ai_model and len(expression) > 10:
                try:
                    explanation = ask_ai(f"Briefly explain this calculation: {expression} = {result}", "math explanation")
                    speak(explanation)
                except:
                    pass
        else:
            # Use AI for complex math problems
            if ai_model:
                ai_calc = ask_ai(f"Solve this math problem and explain briefly: {expression}", "mathematics")
                speak(ai_calc)
            else:
                speak("Invalid calculation expression")
    except Exception as e:
        if ai_model:
            try:
                ai_help = ask_ai(f"Help solve this math problem: {expression}", "mathematics")
                speak(ai_help)
            except:
                speak("I couldn't calculate that")
        else:
            speak("I couldn't calculate that")

def create_folder(command):
    """Creates a new folder based on a voice command."""
    try:
        # Clean up the command to extract the core request
        command = command.lower()
        phrases_to_remove = ["creator folder called", "create a folder named", "create a folder called", "create folder", "make a folder named", "make a folder called", "make folder"]
        for phrase in phrases_to_remove:
            if phrase in command:
                command = command.replace(phrase, "").strip()

        # Logic to separate folder name from path
        # e.g., "my_folder in D drive" or "my_folder"
        parts = command.split(" in ")
        folder_name = parts[0].strip()
        path = "."  # Default to current directory

        if len(parts) > 1:
            path_str = parts[1].strip()
            # Handles "D drive", "the D drive"
            if "drive" in path_str:
                # Find the drive letter, which should be the first letter
                for char in path_str:
                    if char.isalpha():
                        drive_letter = char.upper()
                        path = f"{drive_letter}:\\"
                        break
            else:
                path = path_str

        # Construct the full path and create the directory
        full_path = os.path.join(path, folder_name)

        if not folder_name:
             speak("Please specify a folder name.")
             return

        if not os.path.exists(full_path):
            os.makedirs(full_path)
            speak(f"Folder '{folder_name}' created successfully at '{os.path.abspath(full_path)}'")
        else:
            speak(f"Folder '{folder_name}' already exists at '{os.path.abspath(full_path)}'")

    except Exception as e:
        print(f"Error creating folder: {e}")
        speak("Sorry, I couldn't create the folder. Please check the name and path provided.")


def create_file(command):
    """Creates a new file with optional content from a command."""
    try:
        # "create file test.txt"
        # "create file report.txt with content Hello World"
        command = command.replace("create file", "").strip()
        parts = command.split(" with content ")
        filename = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ""

        if not filename:
            speak("Please specify a filename.")
            return

        with open(filename, 'w') as f:
            f.write(content)
        speak(f"File '{filename}' created successfully.")
    except Exception as e:
        print(f"Error creating file: {e}")
        speak(f"Failed to create file '{filename}'.")

def list_files(directory="."):
    """Lists files in a directory."""
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        if files:
            speak(f"Found {len(files)} files:")
            for file in files[:5]:  # Limit to first 5 files
                speak(file)
            if len(files) > 5:
                speak(f"And {len(files) - 5} more files")
        else:
            speak("No files found in this directory")
    except Exception as e:
        speak("Unable to list files")

# -------------------
# 3. CORE COMMAND FUNCTIONS (Enhanced with AI)
# -------------------

def open_website(url, name):
    """Opens a website in the default browser."""
    speak(f"Opening {name}")
    webbrowser.open(url)

def google_search(query):
    """Performs a Google search with AI enhancement."""
    if not query:
        speak("What would you like me to search for?")
        query = listen()
        if not query:
            return
    
    # Extract search term from command
    search_terms = ["search for", "google", "search", "look up", "find"]
    for term in search_terms:
        if term in query:
            query = query.replace(term, "").strip()
            break
    
    speak(f"Searching Google for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    
    # AI context about the search
    if ai_model:
        try:
            context = ask_ai(f"Provide a brief overview of what someone might find when searching for: {query}", "search context")
            speak(f"You should find information about: {context}")
        except:
            pass

def play_youtube_video(query):
    """Plays a video on YouTube."""
    if not query:
        speak("What video should I play on YouTube?")
        query = listen()
        if not query:
            return
    
    # Extract video name from command
    play_terms = ["play", "youtube", "video"]
    for term in play_terms:
        if term in query:
            query = query.replace(term, "").strip()
    
    speak(f"Playing {query} on YouTube")
    try:
        pywhatkit.playonyt(query)
    except Exception as e:
        speak("Unable to play the video. Opening YouTube search instead")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")

def get_weather(city):
    """Enhanced weather function with AI interpretation."""
    if not city:
        speak("Which city's weather would you like to know?")
        city = listen()
        if not city:
            return
    
    # Extract city name from command
    weather_terms = ["weather in", "weather", "temperature in", "climate in"]
    for term in weather_terms:
        if term in city:
            city = city.replace(term, "").strip()
    
    api_key = CONFIG.get("api_keys", {}).get("openweathermap")
    if not api_key or "YOUR_WEATHER_API_KEY" in api_key:
        # Use AI as fallback
        if ai_model:
            ai_weather = ask_ai(f"What's the general weather like in {city}? Provide current season information and typical weather patterns.", "weather information")
            speak(f"I don't have real-time weather data, but here's what I can tell you about {city}: {ai_weather}")
        else:
            speak("Weather API key not configured. Please add it to config.json")
        return
        
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    
    try:
        response = requests.get(base_url, params=params).json()
        if response.get("cod") == 200:
            weather_desc = response["weather"][0]["description"]
            temp = response["main"]["temp"]
            feels_like = response["main"]["feels_like"]
            humidity = response["main"]["humidity"]
            
            basic_weather = f"The weather in {city} is currently {weather_desc} with a temperature of {temp:.0f} degrees Celsius. It feels like {feels_like:.0f} degrees with {humidity}% humidity."
            speak(basic_weather)
            
            # AI recommendation
            if ai_model:
                try:
                    recommendation = ask_ai(f"Given this weather in {city}: {weather_desc}, {temp}°C, {humidity}% humidity, what clothing or activity recommendations would you give?", "weather advice")
                    speak(f"Recommendation: {recommendation}")
                except:
                    pass
        else:
            speak(f"Sorry, I couldn't find the weather for {city}")
    except requests.exceptions.RequestException:
        speak("Sorry, I couldn't connect to the weather service")

def search_wikipedia(query):
    """Enhanced Wikipedia search with AI summarization."""
    if not query:
        speak("What would you like me to look up on Wikipedia?")
        query = listen()
        if not query:
            return
    
    # Extract search term from command
    wiki_terms = ["wikipedia", "who is", "what is", "tell me about", "search wikipedia for"]
    for term in wiki_terms:
        if term in query:
            query = query.replace(term, "").strip()
    
    try:
        speak(f"Searching Wikipedia for {query}")
        result = wikipedia.summary(query, sentences=2, auto_suggest=True)
        speak("According to Wikipedia:")
        speak(result)
        
        # AI additional context
        if ai_model:
            try:
                additional_info = ask_ai(f"Add interesting context or related information about: {query}", "educational context")
                speak(f"Additional context: {additional_info}")
            except:
                pass
                
    except wikipedia.exceptions.PageError:
        if ai_model:
            ai_info = ask_ai(f"Provide information about: {query}", "educational information")
            speak(f"I couldn't find a Wikipedia page, but here's what I know: {ai_info}")
        else:
            speak(f"Sorry, I couldn't find a Wikipedia page for {query}")
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"That could mean several things, such as {e.options[0]} or {e.options[1]}. Please be more specific")

def adjust_volume(command_str):
    """Adjusts system volume (Windows Only)."""
    if sys.platform != "win32":
        speak("Volume control is currently only supported on Windows")
        return
        
    if not PYCAW_INSTALLED:
        speak("Volume control libraries not installed. Please run: pip install pycaw comtypes")
        return

    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_level_scalar = volume.GetMasterVolumeLevelScalar()
        
        # Extract numbers from command
        numbers = []
        for word in command_str.split():
            cleaned_word = ''.join(filter(str.isdigit, word))
            if cleaned_word:
                numbers.append(int(cleaned_word))
        
        # Set volume to specific level
        if ("set to" in command_str or "to" in command_str) and numbers:
            level_to_set = numbers[0]
            if 0 <= level_to_set <= 100:
                volume.SetMasterVolumeLevelScalar(level_to_set / 100.0, None)
                speak(f"Volume set to {level_to_set} percent")
            else:
                speak("Please specify a volume level between 0 and 100")
            return

        # Increase volume
        if "increase" in command_str or "up" in command_str:
            change_percent = numbers[0] if numbers and "by" in command_str else 10
            new_level = min(1.0, current_level_scalar + (change_percent / 100.0))
            volume.SetMasterVolumeLevelScalar(new_level, None)
            speak(f"Increased volume to {int(new_level * 100)} percent")
            return

        # Decrease volume
        if "decrease" in command_str or "down" in command_str:
            change_percent = numbers[0] if numbers and "by" in command_str else 10
            new_level = max(0.0, current_level_scalar - (change_percent / 100.0))
            volume.SetMasterVolumeLevelScalar(new_level, None)
            speak(f"Decreased volume to {int(new_level * 100)} percent")
            return

        # Set to specific number
        if numbers:
            level_to_set = numbers[0]
            if 0 <= level_to_set <= 100:
                volume.SetMasterVolumeLevelScalar(level_to_set / 100.0, None)
                speak(f"Volume set to {level_to_set} percent")
            else:
                speak("Please specify a volume level between 0 and 100")
            return

        speak("Sorry, I didn't understand how to adjust the volume. Try 'increase volume', 'decrease by 20', or 'set volume to 50'")

    except Exception as e:
        speak("Sorry, I had trouble adjusting the volume")

def toggle_mute():
    """Mutes or unmutes the system volume (Windows Only)."""
    if sys.platform != "win32":
        speak("Mute control is currently only supported on Windows")
        return
        
    if not PYCAW_INSTALLED:
        speak("Volume control libraries not installed. Please run: pip install pycaw comtypes")
        return
        
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        is_muted = volume.GetMute()
        volume.SetMute(not is_muted, None)
        speak("Muted" if not is_muted else "Unmuted")
    except Exception as e:
        speak("Sorry, I had trouble with the mute function")

def system_power(action):
    """Shuts down or restarts the computer after confirmation."""
    if action not in ["shutdown", "restart"]:
        return
        
    speak(f"Are you sure you want to {action} the computer? Please say 'yes' to confirm")
    confirmation = listen()
    
    if confirmation and "yes" in confirmation:
        speak(f"{action.capitalize()}ing the computer in 5 seconds")
        if sys.platform == "win32":
            cmd = "shutdown /s /t 5" if action == "shutdown" else "shutdown /r /t 5"
            os.system(cmd)
        else:
            os.system("sudo " + ("poweroff" if action == "shutdown" else "reboot"))
    else:
        speak(f"{action.capitalize()} cancelled")

# -------------------
# 4. ENHANCED COMMAND FUNCTIONS
# -------------------

def smart_app_opener(app_name):
    """Enhanced app opener with better error handling and more apps."""
    paths = CONFIG.get("app_paths", {})
    app_name = app_name.lower()
    
    # Handle common variations
    app_aliases = {
        "code": "vscode",
        "visual studio code": "vscode",
        "google chrome": "chrome",
        "mozilla firefox": "firefox",
        "calc": "calculator",
        "note": "notepad"
    }
    
    actual_app = app_aliases.get(app_name, app_name)
    path = paths.get(actual_app)
    
    if not path:
        speak(f"I don't know how to open {app_name}. Please add it to your config file.")
        return

    if not os.path.exists(path):
        speak(f"The path for {app_name} seems incorrect. Please check your config file.")
        return
        
    try:
        speak(f"Opening {app_name}")
        if sys.platform == "win32":
            if actual_app == "discord":
                subprocess.Popen([path, "--processStart", "Discord.exe"])
            else:
                os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        speak(f"Failed to open {app_name}")

def uninstall_application(command):
    """
    Finds and runs the uninstaller for a given application silently.
    This feature is for Windows only and requires administrative privileges.
    """
    if sys.platform != "win32":
        speak("This feature is only available on Windows.")
        return

    app_name = command.replace("uninstall", "").strip()
    if not app_name:
        speak("Which application would you like to uninstall?")
        app_name = listen()
        if not app_name:
            return

    speak(f"Are you absolutely sure you want to uninstall {app_name}? This cannot be undone. Please say 'yes' to confirm.")
    confirmation = listen()

    if confirmation and "yes" in confirmation:
        speak(f"Searching for the uninstaller for {app_name}. This requires administrative privileges to run.")
        try:
            import winreg
            
            # Paths to the uninstall registry keys
            uninstall_keys = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            uninstall_string = None
            
            for key_path in uninstall_keys:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    # --- FIX: More flexible search logic ---
                                    search_terms = app_name.lower().split()
                                    if all(term in display_name.lower() for term in search_terms):
                                        uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                        break
                                except FileNotFoundError:
                                    continue
                except FileNotFoundError:
                    continue
                if uninstall_string:
                    break

            if uninstall_string:
                # Attempt to make the uninstallation silent
                # This is a heuristic and might not work for all uninstallers
                uninstall_command = uninstall_string.replace('/I', '/X').replace('/i', '/x')
                if "msiexec.exe" in uninstall_command.lower():
                    if "/qn" not in uninstall_command and "/quiet" not in uninstall_command:
                        uninstall_command += " /qn"
                else:
                    if "/S" not in uninstall_command and "/silent" not in uninstall_command:
                        uninstall_command += " /S"

                speak(f"Found the uninstaller. Attempting to run it silently now.")
                print(f"Executing command: {uninstall_command}")
                
                # Running with subprocess.run and capturing output
                result = subprocess.run(uninstall_command, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    speak(f"{app_name} has been successfully uninstalled.")
                else:
                    speak(f"The uninstaller for {app_name} ran, but it might require manual interaction or failed. Please check your system.")
                    # Fallback to opening control panel if silent uninstall fails
                    speak("Opening the Programs and Features window for you.")
                    os.system("control appwiz.cpl")

            else:
                speak(f"I could not find an uninstaller for {app_name}. I will open the Control Panel for you.")
                os.system("control appwiz.cpl")

        except ImportError:
            speak("The 'winreg' module is needed for this feature, which is standard on Windows.")
        except Exception as e:
            print(f"Uninstallation error: {e}")
            speak(f"An error occurred. I'm opening the Control Panel so you can uninstall manually.")
            os.system("control appwiz.cpl")
    else:
        speak("Uninstallation cancelled.")

def switch_to_window(command):
    """Switches focus to a window specified in the command."""
    if not PYGETWINDOW_AVAILABLE:
        speak("Window management is not available. Please install the pygetwindow library by running: pip install pygetwindow")
        return

    try:
        # e.g., "switch to chrome" -> "chrome"
        app_name = command.replace("switch to", "").strip()

        if not app_name:
            speak("Which application would you like to switch to?")
            app_name = listen()
            if not app_name:
                return

        # Find windows that match the name
        windows = gw.getWindowsWithTitle(app_name)

        if windows:
            # Activate the first matching window using a more robust sequence
            target_window = windows[0]
            if target_window.isMinimized:
                target_window.restore()
            time.sleep(0.05) # Add a small delay
            target_window.activate()
            speak(f"Switched to {app_name}")
        else:
            speak(f"Sorry, I couldn't find a window for {app_name}.")

    except Exception as e:
        print(f"Error switching window: {e}")
        speak("I encountered an error while trying to switch windows.")

def close_active_window():
    """Closes the currently active window after confirmation."""
    if not PYGETWINDOW_AVAILABLE:
        speak("Window management is not available. Please install pygetwindow.")
        return

    try:
        active_window = gw.getActiveWindow()
        if active_window:
            # --- FIX: Avoid closing critical system windows ---
            if active_window.title in ["Windows Shell Experience Host", "Program Manager"]:
                speak("I cannot close this window as it is a critical part of the system.")
                return

            speak(f"Are you sure you want to close the window titled '{active_window.title}'? Please say 'yes' to confirm.")
            confirmation = listen()
            if confirmation and "yes" in confirmation:
                active_window.close()
                speak("Window closed.")
            else:
                speak("Close window command cancelled.")
        else:
            speak("I couldn't find an active window to close.")
    except Exception as e:
        print(f"Error closing window: {e}")
        speak("I encountered an error while trying to close the window.")

def recall_fact(command):
    """Recalls a fact from user_memory. If not found, falls back to Wikipedia."""
    try:
        # e.g., "what is my pin" or "who is my wife"
        key = command.lower()
        triggers = ["what is", "what's", "who is", "who's", "tell me about", "tell me"]
        for trigger in triggers:
            if key.startswith(trigger):
                key = key.replace(trigger, "").strip()
                break

        # Check user memory first
        config_data = load_config()
        user_memory = config_data.get("user_memory", {})

        # Find the best match in memory using difflib for fuzzy matching
        stored_keys = list(user_memory.keys())
        matches = difflib.get_close_matches(key, stored_keys, n=1, cutoff=0.6)

        if matches:
            best_match = matches[0]
            value = user_memory[best_match]
            speak(f"You told me that {best_match} is {value}.")
            return

        # If not found in local memory, proceed to other search functions
        speak(f"I don't have '{key}' in my memory. Let me search online for you.")

        # Fallback to existing search functions
        search_wikipedia(command) # Pass the original command for better context

    except Exception as e:
        print(f"Error recalling fact: {e}")
        speak("I had trouble recalling that fact.")

def remember_fact(command):
    """Saves a user-defined fact to the config file."""
    try:
        # e.g., "remember that my pin is 1234"
        # Find the delimiter " is "
        parts = command.lower().split(" is ")
        if len(parts) < 2:
            speak("I didn't understand the format. Please say 'remember that [the fact] is [the value]'.")
            return

        # The key is everything after "remember that" and before "is"
        key_phrase = parts[0]
        # Remove "remember that" and similar phrases
        for trigger_phrase in ["remember that", "remember"]:
             if key_phrase.startswith(trigger_phrase):
                  key = key_phrase.replace(trigger_phrase, "").strip()
                  break
        else:
             key = key_phrase.strip()

        # The value is everything after the first " is "
        value = " is ".join(parts[1:]).strip()

        if not key or not value:
            speak("I seem to be missing either the fact or the value to remember.")
            return

        # Load, update, and save config
        config_data = load_config()
        config_data["user_memory"][key] = value

        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=4)

        speak(f"Got it. I'll remember that {key} is {value}.")

    except Exception as e:
        print(f"Error remembering fact: {e}")
        speak("I had trouble remembering that. Please try again.")

def minimize_all_windows():
    """Minimizes all windows to show the desktop."""
    if not PYAUTOGUI_AVAILABLE:
        speak("Desktop management is not available. Please install pyautogui.")
        return

    try:
        # Use platform-specific hotkeys to show the desktop
        if sys.platform == "win32":
            pyautogui.hotkey('win', 'd')
        elif sys.platform == "darwin":  # macOS
            pyautogui.hotkey('command', 'option', 'h', 'm') # Hides others, not quite the same but close
        else:  # Linux (works on many distros like Ubuntu)
            pyautogui.hotkey('ctrl', 'super', 'd')

        speak("Showing the desktop.")

    except Exception as e:
        print(f"Error minimizing windows: {e}")
        speak("I encountered an error while trying to minimize windows.")

# -------------------
# 5. AI-ENHANCED COMMAND MAPPING
# -------------------

COMMANDS = {
    # Basic interactions with AI enhancement
    ("hello", "hi", "hey", "good morning", "good evening"): lambda: speak(f"Hello! I'm Jarvis, your AI-enhanced voice assistant. How can I help you today?"),
    ("how are you", "how are you doing"): lambda: speak("I'm doing great with my new AI capabilities! Ready to help you with anything you need."),
    ("what can you do", "help", "commands"): lambda: speak("I can open apps, search the web, play videos, check weather, take screenshots, set reminders, tell jokes, perform calculations, answer questions with AI, have conversations, and much more!"),
    
    # AI-specific commands
    ("ask ai", "ai", "artificial intelligence"): lambda cmd: ai_general_query(cmd.replace("ask ai", "").replace("ai", "").strip()),
    ("explain", "tell me about"): lambda cmd: ai_explain_topic(cmd),
    ("help me with", "solve", "problem"): lambda cmd: ai_problem_solver(cmd),
    ("write", "create", "generate"): lambda cmd: ai_creative_task(cmd),
    ("code", "programming", "script"): lambda cmd: ai_code_helper(cmd),
    
    # System control & monitoring
    ("what time is it", "current time", "time"): get_current_time,
    ("system status", "performance", "cpu usage"): get_system_status,
    ("take screenshot", "screenshot"): take_screenshot,
    ("open camera", "camera"): open_camera,
    
    # Web and search
    ("open youtube",): lambda: webbrowser.open("https://www.youtube.com"),
    ("open google",): lambda: webbrowser.open("https://www.google.com"),
    ("open facebook",): lambda: webbrowser.open("https://www.facebook.com"),
    ("open twitter",): lambda: webbrowser.open("https://www.twitter.com"),
    ("open gmail",): lambda: webbrowser.open("https://www.gmail.com"),
    
    # Media and entertainment
    ("play",): play_youtube_video,
    ("tell me a joke", "joke"): get_joke,
    ("news", "latest news", "headlines"): get_news,
    
    # Productivity
    ("search for", "google", "search"): google_search,
    ("smart search",): ai_smart_search,
    ("wikipedia",): search_wikipedia,
    ("calculate", "math", "compute"): calculate,
    ("create file",): create_file,
    ("list files", "show files"): list_files,
    ("remind me", "set reminder"): lambda cmd: handle_reminder(cmd),
    
    # System control
    ("weather in", "weather"): get_weather,
    ("volume", "set volume", "increase volume", "decrease volume"): adjust_volume,
    ("mute", "unmute"): toggle_mute,
    ("shutdown", "shut down"): lambda: system_power("shutdown"),
    ("restart", "reboot"): lambda: system_power("restart"),
    ("uninstall", "remove program"): uninstall_application,
    
    # Apps
    ("open",): lambda cmd: handle_app_opening(cmd),
    
    # Exit commands
    ("exit", "quit", "goodbye", "bye", "stop"): lambda: (speak("Goodbye! Have a great day!"), sys.exit()),
}

def handle_reminder(command):
    """Handles reminder setting commands."""
    try:
        words = command.split()
        if "in" in words:
            in_index = words.index("in")
            minutes = int(words[in_index + 1])
            message = " ".join(words[in_index + 3:])  # Skip "minutes"
            set_reminder(minutes, message)
        else:
            speak("Please say 'remind me in X minutes to do something'")
    except:
        speak("I didn't understand the reminder format")

def handle_app_opening(command):
    """Handles app opening commands."""
    if "open" in command:
        app_name = command.replace("open", "").strip()
        smart_app_opener(app_name)

# -------------------
# 6. ENHANCED LISTENING AND PROCESSING WITH AI
# -------------------

def listen():
    """Enhanced listening with better noise handling."""
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Processing...")
            command = recognizer.recognize_google(audio)
            print(f"✅ You said: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout")
            return ""
        except sr.UnknownValueError:
            print("❓ Didn't catch that")
            return ""
        except sr.RequestError as e:
            speak("Sorry, my speech service is having issues")
            return ""
        except Exception as e:
            print(f"❌ Error in listen(): {e}")
            return ""

def process_command(command):
    """Enhanced command processing with AI fallback."""
    if not command:
        return False

    # --- FIX: Prioritize specific, multi-word commands before generic ones ---
    # Check for specific phrases first to avoid being caught by generic triggers like "create".
    if any(phrase in command for phrase in ["create folder", "make folder", "create a folder"]):
        create_folder(command)
        return True

    # Check for window management commands with flexible matching
    if any(phrase in command for phrase in ["close window", "close the window", "close active window"]):
        close_active_window()
        return True
    if "switch to" in command:
        switch_to_window(command)
        return True
    if any(phrase in command for phrase in ["minimize all", "show desktop"]):
        minimize_all_windows()
        return True

    # Memory commands
    if command.startswith("remember"):
        remember_fact(command)
        return True
    if any(phrase in command for phrase in ["what is", "what's", "who is", "who's", "when is", "when's", "where is", "where's", "tell me"]):
        recall_fact(command)
        return True

    # Find exact matches first
    for triggers, function in COMMANDS.items():
        for trigger in triggers:
            if command.startswith(trigger):
                try:
                    sig = inspect.signature(function)
                    if len(sig.parameters) > 0:
                        function(command)
                    else:
                        function()
                    return True
                except Exception as e:
                    print(f"Error executing command: {e}")
                    speak("I encountered an error while trying to do that")
                    return False

    # If no exact match, try partial matching for common commands
    if any(word in command for word in ["open", "launch", "start"]):
        app_name = command.replace("open", "").replace("launch", "").replace("start", "").strip()
        smart_app_opener(app_name)
        return True
    
    if any(word in command for word in ["calculate", "compute", "math"]):
        # Extract mathematical expression
        math_words = ["calculate", "compute", "math", "what", "is"]
        expression = command
        for word in math_words:
            expression = expression.replace(word, "")
        expression = expression.strip()
        calculate(expression)
        return True

    # AI fallback for unknown commands
    if ai_model and CONFIG.get("preferences", {}).get("ai_fallback", True):
        try:
            print("🤖 Using AI to handle unknown command...")
            
            # First, analyze the command
            analysis = ai_task_analyzer(command)
            
            if analysis:
                category = analysis.split("|")[0].strip()
                
                if category == "SEARCH":
                    google_search(command)
                    return True
                elif category == "CALCULATE":
                    calculate(command)
                    return True
                elif category == "CONVERSATION":
                    ai_general_query(command)
                    return True
                elif category == "OPEN_APP":
                    # Extract app name and try to open
                    words = command.split()
                    app_candidates = [word for word in words if word not in ["open", "launch", "start", "run"]]
                    if app_candidates:
                        smart_app_opener(" ".join(app_candidates))
                        return True
            
            # If analysis doesn't help, use general AI response
            ai_general_query(command)
            return True
            
        except Exception as e:
            print(f"AI fallback error: {e}")
    
    speak(f"I'm not sure how to handle '{command}'. Try saying 'help' to see what I can do, or I can try to help with AI assistance.")
    return False

def test_audio_output():
    """Test different TTS methods to find what works."""
    print("🔊 Testing audio output methods...")
    
    test_text = "Audio test successful"
    
    # Test 1: Windows SAPI
    if sys.platform == "win32":
        try:
            print("🔄 Testing Windows SAPI...")
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(test_text)
            print("✅ Windows SAPI works!")
            return "sapi"
        except Exception as e:
            print(f"❌ Windows SAPI failed: {e}")
    
    # Test 2: pyttsx3
    try:
        print("🔄 Testing pyttsx3...")
        test_engine = pyttsx3.init()
        test_engine.say(test_text)
        test_engine.runAndWait()
        test_engine.stop()
        print("✅ pyttsx3 works!")
        return "pyttsx3"
    except Exception as e:
        print(f"❌ pyttsx3 failed: {e}")
    
    # Test 3: PowerShell
    if sys.platform == "win32":
        try:
            print("🔄 Testing PowerShell TTS...")
            cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{test_text}\')"'
            os.system(cmd)
            print("✅ PowerShell TTS works!")
            return "powershell"
        except Exception as e:
            print(f"❌ PowerShell failed: {e}")
    
    print("❌ No working TTS method found!")
    return None

# -------------------
# 7. MAIN EXECUTION LOOP WITH AI
# -------------------

def main():
    """Enhanced main loop with AI integration."""
    print("🚀 Starting Jarvis 3.0 with AI...")
    
    # Test audio output first
    print("🔊 Testing audio output...")
    working_tts = test_audio_output()
    
    if working_tts:
        print(f"✅ Audio working with {working_tts}")
    else:
        print("❌ No audio output available")
        print("💡 Installing pywin32 might help: pip install pywin32")
    
    # Initialize TTS
    print("🔊 Initializing Text-to-Speech...")
    tts_success = initialize_tts()
    
    # Initialize AI
    print("🤖 Initializing Gemini AI...")
    ai_success = initialize_ai()
    
    if ai_success:
        speak("Jarvis 3.0 is now online with advanced AI capabilities!")
    else:
        speak("Jarvis is online, but AI features are not available.")
    
    speak("I'm your enhanced voice assistant with artificial intelligence!")
    speak("Say my name followed by a command, ask me questions, or have a conversation with me!")
    
    WAKE_WORD = CONFIG.get("preferences", {}).get("wake_word", "jarvis")
    
    consecutive_empty_commands = 0
    
    while True:
        try:
            command_text = listen()
            
            if not command_text:
                consecutive_empty_commands += 1
                if consecutive_empty_commands >= 3:
                    if ai_model:
                        prompt_response = ask_ai("Generate a friendly reminder that you're still available to help, keep it short and varied", "system prompt")
                        speak(prompt_response)
                    else:
                        speak("I'm still here if you need me. Just say my name!")
                    consecutive_empty_commands = 0
                continue
            
            consecutive_empty_commands = 0
            
            if WAKE_WORD in command_text:
                # Find the wake word and extract the command
                wake_index = command_text.find(WAKE_WORD)
                actual_command = command_text[wake_index + len(WAKE_WORD):].strip()
                
                if actual_command:
                    speak("On it!")
                    if process_command(actual_command):
                        completion_responses = [
                            "Task completed! Anything else I can help you with?",
                            "Done! What else can I do for you?",
                            "All set! Need anything else?",
                            "Perfect! What's next?"
                        ]
                        speak(random.choice(completion_responses))
                    else:
                        speak("I couldn't complete that task. Try asking me for help to see what I can do.")
                else:
                    if ai_model:
                        ai_responses = ask_ai("Generate a friendly greeting response for when someone just says 'Jarvis' without a command. Be helpful and encouraging.", "greeting")
                        speak(ai_responses)
                    else:
                        responses = [
                            "Yes, I'm listening! What do you need?",
                            "How can I help you today?",
                            "What can I do for you?",
                            "I'm here and ready to assist!"
                        ]
                        speak(random.choice(responses))
                    
                    # Wait for follow-up command
                    speak("Please tell me what you'd like me to do.")
                    follow_up = listen()
                    if follow_up:
                        if process_command(follow_up):
                            speak("Perfect! What else can I do?")
                        else:
                            speak("I didn't understand that command. Try saying 'help' to see what I can do, or just ask me anything!")
                            
        except KeyboardInterrupt:
            if ai_model:
                farewell = ask_ai("Generate a friendly goodbye message", "farewell")
                speak(farewell)
            else:
                speak("Shutting down Jarvis. Have a wonderful day!")
            break
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            speak("I encountered an unexpected error, but I'm still running and ready to help.")

if __name__ == "__main__":
    # Check for required AI library
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ Google Generative AI library not found!")
        print("💡 Please install it with: pip install google-generativeai")
        print("🔄 Starting without AI features...")
        ai_model = None
    
    main()