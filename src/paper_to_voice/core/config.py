"""
Configuration module for Paper to Voice Assistant
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Set up Google API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

# Model configuration
GOOGLE_MODEL_NAME = os.getenv('GOOGLE_MODEL_NAME', 'gemini-1.5-flash')

# Create LLM instance
def get_llm():
    return ChatGoogleGenerativeAI(
        model=GOOGLE_MODEL_NAME,
        temperature=0,
        max_tokens=None,
        max_retries=2
    )

# TTS Configuration
TTS_MODEL = "myshell-ai/MeloTTS-English"

# Audio Configuration
LIGHT_GUITAR_FREQ = 440
AMBIENT_GUITAR_FREQ = 220
GUITAR_DURATION = 1000  # milliseconds

# File paths
TEMP_DIR = "temp"
VOICES_DIR = "voices"
