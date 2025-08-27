"""
Text-to-Speech functionality using MeloTTS
"""

import time
from gradio_client import Client
from ..core.config import TTS_MODEL


def get_text_to_voice(text: str, speed: float = 0.9, accent: str = "EN-US", language: str = "EN") -> str:
    """
    Convert text to speech using MeloTTS
    
    Args:
        text: Text to convert to speech
        speed: Speaking speed (default: 0.9)
        accent: Voice accent (default: "EN-US")
        language: Language code (default: "EN")
        
    Returns:
        Path to the generated audio file
    """
    hf_client = Client(TTS_MODEL)
    file_path = hf_client.predict(
        text=text,
        language=language,
        speaker=accent,
        speed=speed,
        api_name="/synthesize",
    )
    return file_path


def generate_podcast_audio(text: str, language: str) -> str:
    """
    Generate podcast audio with appropriate voice settings for different speakers
    
    Args:
        text: Text to convert to speech
        language: Language code
        
    Returns:
        Path to generated audio file or 'Empty Text' if no valid text
    """
    if "**Jane:**" in text:
        text = text.replace("**Jane:**", '').strip()
        accent = "EN-US"
        speed = 0.9
    elif "**Dr. Sharma:**" in text:
        text = text.split("**")[-1].strip()
        accent = "EN_INDIA"
        speed = 0.9
    else:
        return 'Empty Text'
    
    # Retry logic for TTS generation
    for attempt in range(3):
        try:
            file_path = get_text_to_voice(text, speed, accent, language)
            return file_path
        except Exception as e:
            if attempt == 2:  # Last attempt
                raise  # Re-raise the last exception if all attempts fail
            time.sleep(1)  # Wait for 1 second before retrying
